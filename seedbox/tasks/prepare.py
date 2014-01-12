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
from six import moves
import rarfile
from oslo.config import cfg

from seedbox.tasks.base import BasePlugin

from seedbox import helpers
from seedbox.common import tools
from seedbox.pluginmanager import register_plugin, phase

__version__ = '2'

log = logging.getLogger(__name__)

# 50 GB Slot Size; very small but provides some
# starting point
DEFAULT_SLOT_SIZE = 50

# 5 GB; 10% of default slot size and provides enough space
# for user to determine if they need to delete something.
DEFAULT_MIN_STORAGE = 5

PLUGIN_OPTS = [
    cfg.BoolOpt(tools.get_disable_optname('CopyFile', __version__),
                default=False,
                help='disable this plugin'),
    cfg.BoolOpt(tools.get_disable_optname('UnrarFile', __version__),
                default=False,
                help='disable this plugin'),
]

cfg.CONF.register_opts(PLUGIN_OPTS, group='plugins')

OPTS = [
    cfg.IntOpt('slot_size',
               default=DEFAULT_SLOT_SIZE,
               help='storage (GB) allocated to seedbox slot'),
    cfg.IntOpt('min_storage_threshold',
               default=DEFAULT_MIN_STORAGE,
               help='minimum storage (GB) threshold before processing stops'),
    cfg.BoolOpt('storage_check_override',
                default=False,
                help='flag to override checking storage, if True then '
                     '`min_storage_threshold` must have positive value'),
    cfg.StrOpt('storage_system',
               default=tools.DEFAULT_SYSTEM,
               help='storage system offset (traditional = 1024 bytes), '
                    '(si = 1000 bytes)',
               choices=tools.SYSTEMS),
]

cfg.CONF.register_opts(OPTS, group='prepare')

# make sure the path for unrar is set properly; if we can't find it
# then we'll just have to let it error out and the user will need to figure
# it out on their system.
unrar_exec = tools.get_exec_path('unrar')
if unrar_exec is not None:
    rarfile.UNRAR_TOOL = unrar_exec


class InsufficientStorage(RuntimeError):

    def __init__(self, *args, **kwargs):
        super(InsufficientStorage, self).__init__(*args, **kwargs)


class _Prepare(BasePlugin):

    _VERSION = __version__

    def __init__(self):
        super(_Prepare, self).__init__()
        self.slotsize = cfg.CONF.prepare.slot_size
        self.system = tools.get_system(cfg.CONF.prepare.storage_system)

        # make sure the threshold is a positive value or zero
        if cfg.CONF.prepare.min_storage_threshold >= 0:
            self.threshold = cfg.CONF.prepare.min_storage_threshold
        else:
            self.threshold = 0

        # defaults to False until criteria is met
        self.override = False

        # if the user requests override, they must provide their own
        # storage threshold; even if it is a very small one
        if cfg.CONF.prepare.storage_check_override:
            if self.threshold:
                self.override = True
            else:
                log.warn('storage_check_override configured ON; '
                         '(required) min_storage_threshold > 0. '
                         'Setting storage_check_override to OFF')

        self.slot_10cent = self.slotsize * .1
        self.default_threshold = min(DEFAULT_MIN_STORAGE, self.slot_10cent)

    def _get_avail_storage(self):

        total_used = tools.get_home_disk_usage(self.system)
        total_avail = self.slotsize - total_used
        log.debug('allocated [%s] used [%s] avail [%s]',
                  self.slotsize, total_used, total_avail)

        return total_avail

    def _is_storage_sufficient(self, total_avail):
        """
        apply some basic rules to determine if we should
        proceed with consuming storage.
        """

        result = True

        if total_avail <= 0:
            # out of space
            log.debug('total_avail < 0')
            result = False
        elif total_avail <= self.threshold:
            # getting close to max; probably do not need
            # to chance running out of space
            log.debug('total_avail < user_threshold')
            result = False
        elif total_avail <= self.default_threshold and not self.override:
            # limited space; be cautious and check back
            # and no override requested by user
            # to use override user must provide their own
            # threshold value
            log.debug('total_avail < DEFAULT')
            result = False
        else:
            # plenty of space for now; check back soon
            pass

        log.debug('is_storage_sufficient: %s %s', total_avail, result)
        return result

    def _storage_check_needed(self, size, available):

        size_gb = tools.byte_to_gb(size, system=self.system)

        result = False
        if (available - self.default_threshold) < 2:
            # minimal storage so always check
            log.debug('storage_check_needed: minimal space left')
            result = True

        elif (available - size_gb) <= self.slot_10cent:
            log.debug('storage_check_needed: less than 10% left')
            result = True

        else:
            # nothing change enough; keep default
            pass

        log.debug('storage_check_needed [%s] [%s] [%s]',
                  size_gb, available, result)
        return result

    def _get_media_files(self, torrent):
        raise NotImplementedError

    @phase(name='prepare')
    def execute(self, torrents):
        """
        Base execute method for prepare phase
        """
        processed_torrents = []

        log.trace('starting prepare plugin')
        for torrent in torrents:

            avail_storage = self._get_avail_storage()

            if not self._is_storage_sufficient(avail_storage):
                log.info('Insufficient storage to continue...')
                break

            self.total_size_of_media = 0

            try:
                log.debug('processing media files for torrent %s', torrent)
                media_files = self._get_media_files(torrent)

                # now loop through the files we got back, if none then
                # no files were in need of copying
                for media_file in media_files:

                    if self._storage_check_needed(self.total_size_of_media,
                                                  avail_storage):
                        log.debug('Total Media (GB): %s',
                                  tools.byte_to_gb(self.total_size_of_media,
                                                   system=self.system))

                        avail_storage = self._get_avail_storage()

                        if not self._is_storage_sufficient(avail_storage):
                            log.info('Insufficient storage to continue...')
                            raise InsufficientStorage(
                                'Insufficient storage to continue: [%s]',
                                avail_storage)

                    # perform execution of task related to associated
                    # files on the filesystem.
                    files = self._execute(media_file)

                    # we need to add new mediafiles to torrent since we
                    # left the previous files in place and created new
                    # ones for the purposes of further procesing later.
                    helpers.add_mediafiles_to_torrent(
                        torrent, cfg.CONF.sync_path, files)

                    # need to show we completed the process;
                    # so show it as synced which is technically true since
                    # we synced it to the sync path.
                    helpers.synced_media_file(media_file)

                else:
                    # after we are done processing the torrent added it the
                    # list of processed torrents; if a break happens
                    # then it will NOT be added to processed list
                    processed_torrents.append(torrent)

            except Exception as err:
                log.debug(
                    'torrent:[{0}] media_files:[{1}] stacktrace: {2}'.format(
                        torrent, media_files, traceback.format_exc()))
                log.info('%s was unable to process %s due to [%s]',
                         self.__class__.__name__, torrent, err)
                # TODO: need to refine this further so we know what
                # errors really happened
                helpers.set_torrent_failed(torrent, err)

        log.trace('ending copy file plugin')
        return processed_torrents


class CopyFile(_Prepare):
    """
    .. note::
        v2 of the copy task
    """

    def __init__(self):
        """
        """
        super(CopyFile, self).__init__()

    def _get_media_files(self, torrent):

        def matches(media_file):
            # if the path is sync_path then it was
            # already processed so remove it from the
            # list of possible media files to process
            if media_file.file_path == cfg.CONF.sync_path:
                return False
            return True

        return list(moves.filter(matches,
                                 helpers.get_media_files(
                                     torrent,
                                     file_exts=tools.format_file_ext(
                                         cfg.CONF.video_filetypes))))

    def _execute(self, media_file):

        # add the size of this media file to the total
        self.total_size_of_media += media_file.size

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
        return [os.path.basename(media_file.filename)]

register_plugin(CopyFile, tools.get_plugin_name('CopyFile', __version__))


class UnrarFile(_Prepare):
    """
    .. note::
        v2 of the unrar task
    """

    def __init__(self):
        """
        """
        super(UnrarFile, self).__init__()

    def _get_media_files(self, torrent):
        return helpers.get_media_files(torrent, compressed=True)

    def _execute(self, media_file):

        log.trace('unrar file: %s', media_file.filename)
        archived_files = None
        with rarfile.RarFile(
                os.path.join(
                    media_file.file_path,
                    media_file.filename)) as compressed_file:

            # add the size of this media file to the total
            self.total_size_of_media += sum(
                rar_info.file_size for rar_info in
                compressed_file.infolist())

            archived_files = compressed_file.namelist()
            compressed_file.extractall(path=cfg.CONF.sync_path)

        return archived_files

register_plugin(UnrarFile, tools.get_plugin_name('UnrarFile', __version__))
