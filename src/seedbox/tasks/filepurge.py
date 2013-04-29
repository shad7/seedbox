"""
filepurge will encapsulate determining what files are no longer in completed
and therefore can be purged from the working cache.
"""
from __future__ import absolute_import
import logging

from seedbox import helpers
from seedbox.pluginmanager import register_plugin, phase

__version__ = '0.1'

log = logging.getLogger(__name__)

class PurgeFile(object):
    """
    Encapsulates the purge identification command
    """

    @phase(name='complete', priority=-1)
    def execute(self, torrents, configs):
        """
        perform the delete of a file
        """
        processed_torrents = []

        # need to backup the databaes before we start purging anything otherwise
        # we could have real issues later on.
        helpers.perform_db_backup(configs.resource_path)

        log.trace('starting purge file plugin.')
        for torrent in torrents:

            try:
                log.debug('checking if purgeable torrent %s', torrent)
    
                if helpers.is_torrent_purgeable(torrent):
                    log.debug('purging media files')
                    helpers.purge_media_files(torrent)
    
                # after we are done processing the torrent added it the list of
                # processed torrents
                processed_torrents.append(torrent)
    
            except Exception as err:
                # TODO: need to refine this further so we know what errors really happened
                helpers.set_torrent_failed(torrent, err)

        log.trace('ending purge file plugin')
        return processed_torrents


register_plugin(PurgeFile)

