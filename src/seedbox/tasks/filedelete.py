"""
filedelete will encapsulate the deleting of files from sync directory once
synce process has completed successfully. Also managing the cache of the file
and corresponding state.
"""
from __future__ import absolute_import
import logging
import os

from seedbox import helpers
from seedbox.pluginmanager import register_plugin, phase

__version__ = '0.1'

log = logging.getLogger(__name__)

class DeleteFile(object):
    """
    Encapsulates the delete command
    """

    @phase(name='complete')
    def execute(self, torrents, configs):
        """
        perform the delete of a file
        """
        processed_torrents = []

        log.trace('starting delete file plugin.')
        for torrent in torrents:

            try:
                log.debug('deleting media files for torrent %s', torrent)
                media_files = helpers.get_media_files(torrent, synced=True)
    
                # now loop through the files we got back, if none then no files
                # were in need of deleting
                for media_file in media_files:
                    log.trace('delete file: %s', media_file.filename)
                    os.remove(os.path.join(configs.sync_path, media_file.filename))
                
                # after we are done processing the torrent added it the list of
                # processed torrents
                processed_torrents.append(torrent)

            except Exception as err:
                log.info('%s was unable to process %s due to [%s]', DeleteFile.__name__, torrent, err)
                # TODO: need to refine this further so we know what errors really happened
                helpers.set_torrent_failed(torrent, err)

        log.trace('ending delete file plugin')
        return processed_torrents

register_plugin(DeleteFile)

