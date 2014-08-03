"""
Public facing database api that leverages a provided implementation to
execute database operations.
"""
import logging
import os

from seedbox import constants
from seedbox.common import timeutil
from seedbox.db import models

LOG = logging.getLogger(__name__)


class DBApi(object):

    """
    Provides API for supported database operations that leverage specified
    implementation.

    :param impl: database plugin instance
    :type impl: :class:`~seedbox.db.base.Connection`
    """

    def __init__(self, impl):
        self.impl = impl

    def clear(self):
        """
        Clears all data from database.
        """
        self.impl.clear()

    def backup(self):
        """Backup database."""
        self.impl.backup()

    def shrink_db(self):
        """Shrink database."""
        self.impl.shrink_db()

    def save_torrent(self, torrent):
        """
        Performs save (insert/update) operation on an instance of torrent.

        :param torrent: an instance of a torrent
        :return: saved torrent instance
        :rtype: :class:`~seedbox.db.models.Torrent`
        """
        return self.impl.save(torrent)

    def bulk_save_torrents(self, value_map, qfilter):
        """
        Performs save (update) operation on multiple instances of torrents
        using the provided data map.

        :param value_map: data attributes and values to update
        :param qfilter: query filter to determine instances to update
        """
        self.impl.bulk_update(value_map, models.Torrent, qfilter)

    def delete_torrent(self, torrent):
        """
        Performs delete operation on specific instance of torrent.

        :param torrent: an instance of torrent
        """
        self.impl.delete(torrent)

    def delete_torrents(self, qfilter):
        """
        Performs delete operation on selection of torrent instances.

        :param qfilter: query filter to determine instances to delete.
        """
        self.impl.delete_by(models.Torrent, qfilter)

    def get_torrents(self, qfilter):
        """
        Perform select operation on selection of torrent instances.

        :param qfilter: query filter to determine instances to fetch.
        :return: torrent instance(s)
        :rtype: :class:`~seedbox.db.models.Torrent`
        """
        return self.impl.fetch_by(models.Torrent, qfilter)

    def get_torrents_active(self):
        """
        Perform select operation using a pre-defined criteria for what
        constitutes an active torrent.

        :return: torrent instance(s)
        :rtype: :class:`~seedbox.db.models.Torrent`
        """
        qfilter = {'and': [{'=': {'invalid': False}},
                           {'=': {'purged': False}},
                           {'=': {'failed': False}},
                           {'in': {'state': constants.ACTIVE_STATES}}
                           ]}
        return self.get_torrents(qfilter)

    def get_torrents_by_state(self, state, failed=False):
        """
        Perform select operation using a pre-defined criteria to get torrents
        by a specific state.

        :param state: name of the state of the torrent
        :param failed: flag indicating to include failed entries or not
        :return: torrent instance(s)
        :rtype: :class:`~seedbox.db.models.Torrent`
        """
        qfilter = {'and': [{'=': {'state': state}},
                           {'=': {'failed': True if failed else False}}
                           ]}
        return self.get_torrents(qfilter)

    def get_torrents_eligible_for_purging(self):
        """
        Perform select operation using a pre-defined criteria for what
        constitutes eligible for purging.

        :return: torrent instance(s)
        :rtype: :class:`~seedbox.db.models.Torrent`
        """
        qfilter = {'and': [{'=': {'invalid': False}},
                           {'=': {'purged': False}},
                           {'in': {'state': constants.INACTIVE_STATES}}
                           ]}
        return self.get_torrents(qfilter)

    def get_torrents_eligible_for_removal(self):
        """
        Perform select operation using a pre-defined criteria for what
        constitutes eligible for removal.

        :return: torrent instance(s)
        :rtype: :class:`~seedbox.db.models.Torrent`
        """
        qfilter = {'and': [{'=': {'purged': True}},
                           {'in': {'state': constants.INACTIVE_STATES}}
                           ]}
        return self.get_torrents(qfilter)

    def get_torrent_by_name(self, name):
        """
        Perform select operation using the name of torrent to fetch torrent.

        :param name: the name of torrent
        :return: torrent instance(s)
        :rtype: :class:`~seedbox.db.models.Torrent`
        """
        qfilter = {'=': {'name': name}}
        return list(self.get_torrents(qfilter))

    def get_torrent(self, torrent_id):
        """
        Perform select operation using the primary key of torrent to fetch
        torrent.

        :param torrent_id: primary key of torrent
        :return: torrent instance(s)
        :rtype: :class:`~seedbox.db.models.Torrent`
        """
        return self.impl.fetch(models.Torrent, torrent_id)

    def fetch_or_create_torrent(self, name):
        """
        Performs select operation using the name of torrent to fetch torrent,
        and if the torrent is not found, then the save (insert) operation is
        performed using the name of the torrent.

        :param name: the name of a torrent
        :return: torrent instance(s)
        :rtype: :class:`~seedbox.db.models.Torrent`
        """
        _torrent = self.get_torrent_by_name(name)
        if not _torrent:
            _torrent = self.save_torrent(models.Torrent(None, name))
        else:
            _torrent = _torrent.pop()
        return _torrent

    def save_media(self, media):
        """
        Perform save (insert/update) operation on an instance of media.

        :param media: an instance of media file
        :return: media file instance
        :rtype: :class:`~seedbox.db.models.MediaFile`
        """
        return self.impl.save(media)

    def bulk_create_medias(self, medias):
        """
        Perform save (insert) operation on a list of instances of media.

        :param medias: a list of instances of media file
        :return: media file instance(s)
        :rtype: :class:`~seedbox.db.models.MediaFile`
        """
        return list(self.impl.bulk_create(medias))

    def delete_media(self, media):
        """
        Perform delete operation on an instance of media.

        :param media: an instance of media file
        """
        self.impl.delete(media)

    def delete_medias(self, qfilter):
        """
        Perform delete operation on a list of instances of media.

        :param qfilter: query filter to determine instances to delete
        """
        self.impl.delete_by(models.MediaFile, qfilter)

    def get_medias(self, qfilter):
        """
        Perform select operation on selection of media instances.

        :param qfilter: query filter to determine instances to fetch.
        :return: media file instance(s)
        :rtype: :class:`~seedbox.db.models.MediaFile`
        """
        return self.impl.fetch_by(models.MediaFile, qfilter)

    def get_medias_by_torrent(self, torrent_id):
        """
        Perform select operation using the primary key of torrent to fetch
        associated media.

        :param torrent_id: primary key of torrent
        :return: media file instance(s)
        :rtype: :class:`~seedbox.db.models.MediaFile`
        """
        qfilter = {'=': {'torrent_id': torrent_id}}
        return self.get_medias(qfilter)

    def get_medias_by(self, torrent_id, file_path=None, compressed=None,
                      synced=None, missing=None, skipped=None):
        """
        Perform select operation using a combination of the provided
        parameters to find specified media.

        :param torrent_id: primary key of torrent
        :param file_path: location where media exist on file system
                          (default: None; ignore attribute)
        :param compressed: flag to indicate to include or exclude compressed
                           media (default: None; ignore attribute)
        :param synced: flag to indicate to include or exclude synced media (
                       default: None; ignored attribute)
        :param missing: flag to indicate to include or exclude missing media
                        (default: None; ignored attribute)
        :param skipped: flag to indicate to include or exclude skipped media
                        (default: None; ignored attribute)
        :return: media file instance(s)
        :rtype: :class:`~seedbox.db.models.MediaFile`
        """
        conditions = [{'=': {'torrent_id': torrent_id}}]
        if file_path is not None:
            conditions.append({'=': {'file_path': file_path}})
        if compressed is not None:
            conditions.append(
                {'=': {'compressed': True if compressed else False}})
        if synced is not None:
            conditions.append({'=': {'synced': True if synced else False}})
        if missing is not None:
            conditions.append({'=': {'missing': True if missing else False}})
        if skipped is not None:
            conditions.append({'=': {'skipped': True if skipped else False}})
        qfilter = {'and': conditions}
        return self.get_medias(qfilter)

    def get_processed_medias(self, torrent_id):
        """
        Performed select operation using torrent primary key and pre-defined
        criteria for what constitutes processed media.

        :param torrent_id: torrent primary key
        :return: media file instance(s)
        :rtype: :class:`~seedbox.db.models.MediaFile`
        """
        qfilter = {'and': [{'=': {'torrent_id': torrent_id}},
                           {'or': [{'=': {'synced': True}},
                                   {'=': {'missing': True}},
                                   {'=': {'skipped': True}}
                                   ]}
                           ]}
        return self.get_medias(qfilter)

    def get_media(self, media_id):
        """
        Perform select operation using media primary key to fetch media.

        :param media_id: media primary key
        :return: media file instance
        :rtype: :class:`~seedbox.db.models.MediaFile`
        """
        return self.impl.fetch(models.MediaFile, media_id)

    def save_appstate(self, appstate):
        """
        Perform save (insert/update) operation on an instance of appstate.

        :param appstate: an instance of appstate
        :return: appstate instance
        :rtype: :class:`~seedbox.db.models.AppState`
        """
        return self.impl.save(appstate)

    def delete_appstate(self, appstate):
        """
        Perform delete operation on an instance of appstate.

        :param appstate: an instance of appstate
        """
        self.impl.delete(appstate)

    def get_appstate(self, name):
        """
        Perform select operation using name of appstate to fetch an instance
        of appstate.

        :param name: name of an appstate instance
        :return: appstate instance
        :rtype: :class:`~seedbox.db.models.AppState`
        """
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
