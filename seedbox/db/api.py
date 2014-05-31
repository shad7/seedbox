import logging
import os

from seedbox import constants
from seedbox.common import timeutil
from seedbox.db import models

LOG = logging.getLogger(__name__)


class DBApi(object):

    def __init__(self, impl):
        self.impl = impl

    def clear(self):
        self.impl.clear()

    def backup(self):
        """Backup database."""
        self.impl.backup()

    def shrink_db(self):
        """Shrink database."""
        self.impl.shrink_db()

    def save_torrent(self, torrent):
        return self.impl.save(torrent)

    def bulk_save_torrents(self, value_map, qfilter):
        self.impl.bulk_update(value_map, models.Torrent, qfilter)

    def delete_torrent(self, torrent):
        self.impl.delete(torrent)

    def delete_torrents(self, qfilter):
        self.impl.delete_by(models.Torrent, qfilter)

    def get_torrents(self, qfilter):
        return self.impl.fetch_by(models.Torrent, qfilter)

    def get_torrents_active(self):
        qfilter = {'and': [{'=': {'invalid': 0}},
                           {'=': {'purged': 0}},
                           {'=': {'failed': 0}},
                           {'in': {'state': constants.ACTIVE_STATES}}
                           ]}
        return self.get_torrents(qfilter)

    def get_torrents_by_state(self, state, failed=False):
        qfilter = {'and': [{'=': {'state': state}},
                           {'=': {'failed': 1 if failed else 0}}
                           ]}
        return self.get_torrents(qfilter)

    def get_torrents_eligible_for_purging(self):
        qfilter = {'and': [{'=': {'invalid': 0}},
                           {'=': {'purged': 0}},
                           {'in': {'state': constants.INACTIVE_STATES}}
                           ]}
        return self.get_torrents(qfilter)

    def get_torrents_eligible_for_removal(self):
        qfilter = {'and': [{'=': {'purged': 1}},
                           {'in': {'state': constants.INACTIVE_STATES}}
                           ]}
        return self.get_torrents(qfilter)

    def get_torrent_by_name(self, name):
        qfilter = {'=': {'name': name}}
        return list(self.get_torrents(qfilter))

    def get_torrent(self, torrent_id):
        return self.impl.fetch(models.Torrent, torrent_id)

    def fetch_or_create_torrent(self, name):
        _torrent = self.get_torrent_by_name(name)
        if not _torrent:
            _torrent = self.save_torrent(models.Torrent(None, name))
        else:
            _torrent = _torrent.pop()
        return _torrent

    def save_media(self, media):
        return self.impl.save(media)

    def bulk_create_medias(self, medias):
        return list(self.impl.bulk_create(medias))

    def delete_media(self, media):
        self.impl.delete(media)

    def delete_medias(self, qfilter):
        self.impl.delete_by(models.MediaFile, qfilter)

    def get_medias(self, qfilter):
        return self.impl.fetch_by(models.MediaFile, qfilter)

    def get_medias_by_torrent(self, torrent_id):
        qfilter = {'=': {'torrent_id': torrent_id}}
        return self.get_medias(qfilter)

    def get_medias_by(self, torrent_id, file_path=None, compressed=None,
                      synced=None, missing=None, skipped=None):
        conditions = [{'=': {'torrent_id': torrent_id}}]
        if file_path is not None:
            conditions.append({'=': {'file_path': file_path}})
        if compressed is not None:
            conditions.append({'=': {'compressed': 1 if compressed else 0}})
        if synced is not None:
            conditions.append({'=': {'synced': 1 if synced else 0}})
        if missing is not None:
            conditions.append({'=': {'missing': 1 if missing else 0}})
        if skipped is not None:
            conditions.append({'=': {'skipped': 1 if skipped else 0}})
        qfilter = {'and': conditions}
        return self.get_medias(qfilter)

    def get_processed_medias(self, torrent_id):
        qfilter = {'and': [{'=': {'torrent_id': torrent_id}},
                           {'or': [{'=': {'synced': 1}},
                                   {'=': {'missing': 1}},
                                   {'=': {'skipped': 1}}
                                   ]}
                           ]}
        return self.get_medias(qfilter)

    def get_media(self, media_id):
        return self.impl.fetch(models.MediaFile, media_id)

    def save_appstate(self, appstate):
        return self.impl.save(appstate)

    def delete_appstate(self, appstate):
        self.impl.delete(appstate)

    def get_appstate(self, name):
        return self.impl.fetch(models.AppState, name)

    def clean_up(self):
        """
        Periodically check for data no longer needed (fully processed,
        invalid, or deleted) and then remove from the database.
        """
        LOG.debug('starting perform_db_cleanup...')

        lpd = self.get_appstate('last_purge_date')
        last_purge_date = lpd.value if lpd else None
        LOG.debug('last_purge_date: %s', last_purge_date)

        if last_purge_date is None:
            LOG.info('First running...setting last purge date to now')
            # never been purged so need to set an initial date (today)
            self.save_appstate(models.AppState('last_purge_date',
                                               timeutil.utcnow()))
            return

        if timeutil.is_older_than(last_purge_date, timeutil.ONE_WEEK):
            LOG.debug('last purge > 1 week ago....ready for some clean up.')
            # ready to start purge process....
            torrents = list(self.get_torrents_eligible_for_purging())
            if torrents:
                LOG.debug('found torrents eligible for purging: %s',
                          len(torrents))
                # perform database backup
                self.backup()

                LOG.debug('purging media associated with torrents....')
                qfilter = {
                    'in': {'torrent_id': [tor.torrent_id for tor in torrents]}
                    }
                self.delete_medias(qfilter)

                qfilter = {
                    'in': {'id': [tor.torrent_id for tor in torrents]}
                    }
                self.bulk_save_torrents({'purged': True}, qfilter)

                # now reset the last purge date to now.
                self.save_appstate(models.AppState('last_purge_date',
                                                   timeutil.utcnow()))

            else:
                # no torrents eligible for purging
                LOG.debug('no torrents found eligible for purging...')

        # done deleting mediafiles; now delete any torrents that were
        # found to be missing from filesystem thereby no longer in
        # need of caching.
        torrents_to_delete = []
        for torrent in self.get_torrents_eligible_for_removal():
            if not os.path.exists(os.path.join(
                    self.impl.conf.torrent.torrent_path, torrent.name)):
                # actual torrent file no longer exists so we can safely
                # delete the torrent from cache
                torrents_to_delete.append(torrent.torrent_id)

        if torrents_to_delete:
            LOG.debug('found torrents eligible for removal: %s',
                      len(torrents_to_delete))
            self.delete_torrents({'in': {'id': torrents_to_delete}})

        LOG.debug('perform_db_cleanup completed')
