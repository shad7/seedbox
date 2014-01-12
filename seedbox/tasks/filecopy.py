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
from oslo.config import cfg

from seedbox.tasks.base import BasePlugin

from seedbox import helpers
from seedbox.common import tools
from seedbox.pluginmanager import register_plugin, phase

__version__ = '1'

log = logging.getLogger(__name__)

PLUGIN_OPTS = [
    cfg.BoolOpt(tools.get_disable_optname('CopyFile', __version__),
                default=False,
                help='disable this plugin'),
]

cfg.CONF.register_opts(PLUGIN_OPTS, group='plugins')


class CopyFile(BasePlugin):
    """
    .. note::
        v1 of copy task
    """
    _VERSION = __version__

    def __init__(self):
        """
        """
        super(CopyFile, self).__init__()

    @phase(name='prepare')
    def execute(self, torrents):
        """
        perform the copy of a file
        """
        processed_torrents = []

        log.trace('starting copy file plugin')
        for torrent in torrents:

            try:
                log.debug('copying media files for torrent %s', torrent)
                media_files = helpers.get_media_files(
                    torrent, file_exts=tools.format_file_ext(
                        cfg.CONF.video_filetypes))

                # now loop through the files we got back, if none then
                # no files were in need of copying
                for media_file in media_files:

                    if media_file.file_path == cfg.CONF.sync_path:
                        log.debug('media file %s already copied; skipping',
                                  media_file)
                        continue
                    log.trace('copying file: %s', media_file.filename)
                    shutil.copy2(
                        os.path.join(media_file.file_path,
                                     media_file.filename),
                        cfg.CONF.sync_path)

                    # we are copying the files not the paths; if the filename
                    # includes path information we will need to strip it for
                    # future consumption when we create the new file entry.
                    # The helper method expects a list but in our case it is
                    # just a single file so wrap it up!
                    helpers.add_mediafiles_to_torrent(
                        torrent, cfg.CONF.sync_path,
                        [os.path.basename(media_file.filename)])
                    # need to show we completed the copy process;
                    # so show it as synced which is technically true since
                    # we synced it to the sync path.
                    helpers.synced_media_file(media_file)

                # after we are done processing the torrent added it the
                # list of processed torrents
                processed_torrents.append(torrent)

            except Exception as err:
                log.debug(
                    'torrent:[{0}] media_files:[{1}] stacktrace: {2}'.format(
                        torrent, media_files, traceback.format_exc()))
                log.info('%s was unable to process %s due to [%s]',
                         CopyFile.__name__, torrent, err)
                # TODO: need to refine this further so we know what
                # errors really happened
                helpers.set_torrent_failed(torrent, err)

        log.trace('ending copy file plugin')
        return processed_torrents

register_plugin(CopyFile, tools.get_plugin_name('CopyFile', __version__))
