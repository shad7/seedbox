"""
filedecompress ecapsulates the decompressing (unrar) command of files
in the completed directory to the sync directory. Also managing the
cache of the file and corresponding state.
"""
from __future__ import absolute_import
import logging
import os
import traceback
import rarfile

from seedbox import helpers, tools
from seedbox.pluginmanager import register_plugin, phase

__version__ = '0.1'

log = logging.getLogger(__name__)

# make sure the path for unrar is set properly; if we can't find it
# then we'll just have to let it error out and the user will need to figure
# it out on their system.
unrar_exec = tools.get_exec_path('unrar')
if unrar_exec is not None:
    rarfile.UNRAR_TOOL = unrar_exec

class UnrarFile(object):
    """
    Encapsulates the unrar command
    """

    @phase(name='prepare')
    def execute(self, torrents, configs):
        """
        perform the unrar of a file
        """
        processed_torrents = []

        log.trace('starting unrar file plugin.')
        for torrent in torrents:

            try:
                log.debug('unrar media files for torrent %s', torrent)
                media_files = helpers.get_media_files(torrent, compressed=True)
    
                # now loop through the files we got back, if none then no files
                # were in need of unraring
                for media_file in media_files:
                    log.trace('unrar file: %s', media_file.filename)
                    with rarfile.RarFile(os.path.join(media_file.file_path, media_file.filename)) as compressed_file:
                        archived_files = compressed_file.namelist()
                        compressed_file.extractall(path=configs.sync_path)
                        helpers.add_mediafiles_to_torrent(torrent, configs.sync_path, archived_files)
                        # need to show we completed the unrar process; so show it as synced
                        # which is technically true since we synced it to the sync path.
                        helpers.synced_media_file(media_file)

                
                # after we are done processing the torrent added it the list of
                # processed torrents
                processed_torrents.append(torrent)
    
            except Exception as err:
                log.debug('torrent: [{0}] media_files: [{1}] stacktrace: {2}'.format(torrent,
                    media_files, traceback.format_exec()))
                log.info('%s was unable to process %s due to [%s]', UnrarFile.__name__, torrent, err)
                # TODO: need to refine this further so we know what errors really happened
                helpers.set_torrent_failed(torrent, err)

        log.trace('ending unrar file plugin')
        return processed_torrents


register_plugin(UnrarFile)

