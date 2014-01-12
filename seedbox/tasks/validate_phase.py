"""
built-in plugin to handle validating if all of the torrents remaining after
all other plugins are processed have completed should be allowed to continue
based on certain validation rules.
"""
from __future__ import absolute_import
import logging
from oslo.config import cfg

from seedbox.tasks.base import BasePlugin

from seedbox import helpers
from seedbox.common import tools
from seedbox.pluginmanager import register_plugin, phase

__version__ = '1'

log = logging.getLogger(__name__)

PLUGIN_OPTS = [
    cfg.BoolOpt(tools.get_disable_optname('PhaseValidator', __version__),
                default=False,
                help='disable this plugin'),
]

cfg.CONF.register_opts(PLUGIN_OPTS, group='plugins')


class PhaseValidator(BasePlugin):
    """
    encapsulation of validation rules for torrents to proceed to the next
    state/phase of processing in our task flow. The priority will ensure
    this is always the very last plugin executed for each phase.
    """
    _VERSION = __version__

    def __init__(self):
        """
        """
        super(PhaseValidator, self).__init__()

    @phase(name='prepare', priority=-999)
    def validate_init(self, torrents):
        """
        Verify the torrents have completed all successfully before allowing
        them to continue to next phase
        """
        valid_torrents = []

        for torrent in torrents:

            # if the torrent is proceeding past init to active, then there
            # must be a file that is NOT missing, NOT skipped, NOT synced,
            # and file_path = sync_path this would mean the file was copied
            # properly to sync path or decompressed to the sync path and is
            # ready for sync. If no files are in this state then the torrent
            # did not successfully complete this phase and should not be
            # moved to the next phase.
            media_files = helpers.get_media_files(
                torrent, file_path=cfg.CONF.sync_path, compressed=None,
                synced=False)

            if media_files:
                log.debug('%s has completed phase prepare successfully',
                          torrent)
                valid_torrents.append(torrent)
            else:
                log.info('%s has failed to complete phase prepare.', torrent)

        return valid_torrents

    @phase(name='activate', priority=-999)
    def validate_active(self, torrents):
        """
        Verify the torrents have completed all successfully before allowing
        them to continue to next phase
        """
        valid_torrents = []

        for torrent in torrents:

            # performs a check to determine if all files have been processed;
            # if so then the activate phase has been completed for this
            # torrent so we will include it. Else it has further processing
            # and should not be included in those torrents going to the
            # next phase.
            if helpers.is_torrent_processed(torrent):
                log.debug('%s has completed phase activate successfully',
                          torrent)
                valid_torrents.append(torrent)
            else:
                log.info('%s has failed to complete phase activate.', torrent)

        return valid_torrents

    @phase(name='complete', priority=-999)
    def validate_done(self, torrents):
        """
        Verify the torrents have completed all successfully before allowing
        them to continue to next phase
        """

        # for now there is nothing really to check that wasn't already check
        # prior to this phase getting executed. so we will simply return back
        # what was sent to us. Basically a placeholder for now.
        log.debug('validate_done defaults to empty, all torrents returned!')
        return torrents

register_plugin(PhaseValidator,
                tools.get_plugin_name('PhaseValidator', __version__))
