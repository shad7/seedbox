"""
filecopy will encapsulate the copying of files from completed directory to
sync directory when file is not in a compressed format. Also managing the
cache of the file and corresponding state.
"""
from __future__ import absolute_import
import logging
import os
import traceback
import shutil

from seedbox import helpers
from seedbox.pluginmanager import register_plugin, phase

__version__ = '0.1'

log = logging.getLogger(__name__)

class CopyFile(object):
    """
    Encapsulates the copy command
    """
    
    # our list of supported extensions, no need to go copying all files
    supported_exts = ['.mp4', '.avi']

    @phase(name='prepare')
    def execute(self, torrents, configs):
        """
        perform the copy of a file
        """
        processed_torrents = []

        log.trace('starting copy file plugin')
        for torrent in torrents:

            try:
                log.debug('copying media files for torrent %s', torrent)
                media_files = helpers.get_media_files(torrent, file_exts=CopyFile.supported_exts)
    
                # now loop through the files we got back, if none then no files
                # were in need of copying
                for media_file in media_files:
                    log.trace('copying file: %s', media_file.filename)
                    shutil.copy2(os.path.join(media_file.file_path, media_file.filename), configs.sync_path)

                    # we are copying the files not the paths; if the filename includes
                    # path information we will need to strip it for future consumption when we
                    # create the new file entry. The helper method expects a list but in our
                    # case it is just a single file so wrap it up!
                    helpers.add_mediafiles_to_torrent(torrent, configs.sync_path,
                        [os.path.basename(media_file.filename)])
                    # need to show we completed the copy process; so show it as synced
                    # which is technically true since we synced it to the sync path.
                    helpers.synced_media_file(media_file)

                
                helpers.set_media_files_path(configs.sync_path, media_files)

                # after we are done processing the torrent added it the list of
                # processed torrents
                processed_torrents.append(torrent)

            except Exception as err:
                log.debug('torrent: [{0}] media_files: [{1}] stacktrace: {2}'.format(torrent,
                    media_files, traceback.format_exec()))
                log.info('%s was unable to process %s due to [%s]', CopyFile.__name__, torrent, err)
                # TODO: need to refine this further so we know what errors really happened
                helpers.set_torrent_failed(torrent, err)

        log.trace('ending copy file plugin')
        return processed_torrents

register_plugin(CopyFile)

