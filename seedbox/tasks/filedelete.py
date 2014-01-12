"""
filedelete will encapsulate the deleting of files from sync directory once
synce process has completed successfully. Also managing the cache of the file
and corresponding state.
"""
from __future__ import absolute_import
import logging
import os
import traceback
from oslo.config import cfg

from seedbox.tasks.base import BasePlugin

from seedbox import helpers
from seedbox.common import tools
from seedbox.pluginmanager import register_plugin, phase

__version__ = '1'

log = logging.getLogger(__name__)

PLUGIN_OPTS = [
    cfg.BoolOpt(tools.get_disable_optname('DeleteFile', __version__),
                default=False,
                help='disable this plugin'),
]

cfg.CONF.register_opts(PLUGIN_OPTS, group='plugins')


class DeleteFile(BasePlugin):
    """
    .. note::
        v1 of the delete task
    """
    _VERSION = __version__

    def __init__(self):
        """
        """
        super(DeleteFile, self).__init__()

    @phase(name='complete')
    def execute(self, torrents):
        """
        perform the delete of a file
        """
        processed_torrents = []

        log.trace('starting delete file plugin.')
        for torrent in torrents:

            try:
                log.debug('deleting media files for torrent %s', torrent)
                media_files = helpers.get_media_files(
                    torrent, file_path=cfg.CONF.sync_path, synced=True)

                # now loop through the files we got back, if none then no
                # files were in need of deleting
                for media_file in media_files:
                    # if for some reason it doesn't exist then no worries
                    # just skip over it and continue; otherwise delete it
                    if os.path.exists(os.path.join(cfg.CONF.sync_path,
                                                   media_file.filename)):
                        log.trace('delete file: %s', media_file.filename)
                        os.remove(os.path.join(cfg.CONF.sync_path,
                                               media_file.filename))

                # after we are done processing the torrent added it the list
                # of processed torrents
                processed_torrents.append(torrent)

            except Exception as err:
                log.debug(
                    'torrent:[{0}] media_files:[{1}] stacktrace: {2}'.format(
                        torrent, media_files, traceback.format_exc()))
                log.info('%s was unable to process %s due to [%s]',
                         DeleteFile.__name__, torrent, err)
                # TODO: need to refine this further so we know what errors
                # really happened
                helpers.set_torrent_failed(torrent, err)

        log.trace('ending delete file plugin')
        return processed_torrents

register_plugin(DeleteFile, tools.get_plugin_name('DeleteFile', __version__))
