"""
filesync was inspired by a posting for doing something similar
`syncfile <http://filesharingtalk.com/threads/436669-One-way-syncing-downloads-from-seedbox-to-home>`_  # noqa

The filesync module encapsulates the rsync command for doing a sync between
source and destination. Also tracking what has been sync'd given the nature of
seedboxes where things stay for extended periods but the destination files
are usually moved into media libraries.
"""
from __future__ import absolute_import
import logging
import os
import traceback
from collections import namedtuple

from oslo.config import cfg

from seedbox.tasks.base import BasePlugin

from seedbox import helpers
from seedbox.common import tools
from seedbox.pluginmanager import register_plugin, phase
from seedbox.subprocessext import ProcessLogging
from seedbox.pssh import manager
from seedbox.pssh import task


__version__ = '1'

log = logging.getLogger(__name__)

PLUGIN_OPTS = [
    cfg.BoolOpt(tools.get_disable_optname('SyncFile', __version__),
                default=False,
                help='disable this plugin'),
]

cfg.CONF.register_opts(PLUGIN_OPTS, group='plugins')

SYNC_OPTS = [
    cfg.BoolOpt('dryrun',
                default=False,
                help='rsync dryrun option'),
    cfg.BoolOpt('verbose',
                default=False,
                help='rsync verbose option'),
    cfg.BoolOpt('progress',
                default=False,
                help='rsync progress option'),
    cfg.BoolOpt('perms',
                default=True,
                help='rsync perms option'),
    cfg.BoolOpt('delayupdates',
                default=True,
                help='rsync delayupdates option'),
    cfg.BoolOpt('recursive',
                default=True,
                help='rsync recursive option'),
    cfg.StrOpt('chmod',
               default='ugo+rwx',
               help='rsync chmod option'),
    cfg.StrOpt('identity',
               help='rsync-ssh identity option (ssh key)'),
    cfg.StrOpt('port',
               default='22',
               help='rsync-ssh port'),
    cfg.StrOpt('remote_user',
               help='User name on remote system (ssh)'),
    cfg.StrOpt('remote_host',
               help='Host name/IP Address of remote system'),
    cfg.StrOpt('remote_path',
               help='rsync destination path'),
    cfg.BoolOpt('enable_parallel',
                default=True,
                help='flag to enable parallel threads of rsync'),
]

cfg.CONF.register_opts(SYNC_OPTS, group='filesync')

PARALLEL_OPTS = [
    cfg.IntOpt('rsync_threads',
               default=5,
               help='Max number of parallel threads'),
    cfg.IntOpt('thread_timeout',
               default=0,
               help='Timeout (secs) (0 = no timeout)'),
    cfg.StrOpt('stdout_dir',
               help='Output directory for stdout files'),
    cfg.StrOpt('stderr_dir',
               help='Output directory for stderr files'),
    cfg.BoolOpt('print_out',
                default=False,
                help='Write output to stdout'),
    cfg.BoolOpt('stdout_buffer',
                default=False,
                help='Buffer stdout until thread ends'),
    cfg.BoolOpt('stderr_buffer',
                default=False,
                help='Buffer stderr until thread ends'),
    cfg.BoolOpt('stderr_verbose',
                default=True,
                help='Output verbose details about exceptions'),
]

cfg.CONF.register_opts(PARALLEL_OPTS, group='prsync')

_TorrentTask = namedtuple('TorrentTask', ['torrent', 'mediatasks', 'failed'])
_MediaTask = namedtuple('MediaTask', ['name', 'media', 'task'])


class SyncFile(BasePlugin):
    """
    Encapsulates the rsync command with the additional feature of having a
    database cache to track which files were already successfully processed
    so they are not re-processed on future executions when the destination
    copy of the file has been moved or deleted.

    Provided is a subset of the inputs the rsync command actually supports
    but these are the most common ones required.

    * dryrun (rsync: dry-run)
    * verbose
    * progress
    * perms
    * delayupdates (rsync: delay-updates)
    * recursive
    * chmod
    * identity (rsync: rsh=ssh)
    * port (rsync: rsh=ssh)

    """
    _VERSION = __version__

    def __init__(self):
        super(SyncFile, self).__init__()
        self._cmd = None

    @phase(name='activate')
    def execute(self, torrents):
        """
        Action method of the Sync Task that acts as factory to the
        configured implementation.

        :param list torrents:   Torrent instances to process
        :returns:               Torrent instances processed
        :rtype:                 list
        """
        # make sure the command is setup
        self._set_cmd()
        # make a copy of it for the implementors
        cmd = self._cmd[:]

        if cfg.CONF.filesync.enable_parallel:
            impl = ParallelSync(torrents=torrents, cmd=cmd,
                                local_path=cfg.CONF.sync_path,
                                remote_path=cfg.CONF.filesync.remote_path,
                                host=cfg.CONF.filesync.remote_host,
                                user=cfg.CONF.filesync.remote_user)
        else:
            impl = SequentialSync(torrents=torrents, cmd=cmd,
                                  local_path=cfg.CONF.sync_path,
                                  remote_path=cfg.CONF.filesync.remote_path,
                                  host=cfg.CONF.filesync.remote_host,
                                  user=cfg.CONF.filesync.remote_user)

        return impl.execute()

    def _set_cmd(self):
        """
        Generate the rsync command using the instance variables as
        configured by user input or using the defaults we set.
        """
        self._cmd = ['rsync']

        if cfg.CONF.filesync.dryrun:
            self._cmd.append('--dry-run')
        if cfg.CONF.filesync.verbose:
            self._cmd.append('--verbose')
        if cfg.CONF.filesync.progress:
            self._cmd.append('--progress')
        if cfg.CONF.filesync.perms:
            self._cmd.append('--perms')
        if cfg.CONF.filesync.delayupdates:
            self._cmd.append('--delay-updates')
        if cfg.CONF.filesync.recursive:
            self._cmd.append('--recursive')
        if cfg.CONF.filesync.chmod:
            self._cmd.append('--chmod=%s' % cfg.CONF.filesync.chmod)

        if cfg.CONF.filesync.identity or cfg.CONF.filesync.port:
            ssh_cmd = '--rsh=ssh'
            if cfg.CONF.filesync.port:
                ssh_cmd = ssh_cmd + ' -p ' + cfg.CONF.filesync.port
            if cfg.CONF.filesync.identity:
                ssh_cmd = ssh_cmd + ' -i ' + cfg.CONF.filesync.identity

            self._cmd.append(ssh_cmd)

        log.debug('formatted cmd: [%s]', self._cmd)

register_plugin(SyncFile, tools.get_plugin_name('SyncFile', __version__))


class _BaseSync(object):

    def __init__(self, torrents, cmd, local_path, remote_path, host, user):
        self.torrents = torrents
        self._cmd = cmd
        self.local_path = local_path
        self.remote_path = None
        self.host = None
        self.user = None

        self._set_remote(remote_path, host, user)

        self._processed = []

    def _set_remote(self, remote_path, host, user):

        if host is not None:
            self.host = host
        if user is not None:
            self.user = user

        if remote_path is not None:
            # since we are most likely going to do
            # some modification to the path given legacy of
            # parameter; we will copy to another variable
            temp_path = remote_path

            # if either user or host are part of path then
            # we need to remove it for now; will remove in future
            # once we have reached a certain point.
            if '@' in temp_path or ':' in temp_path:
                parts = temp_path.split('@')
                if len(parts) == 2:
                    if self.user is None:
                        self.user = parts[0]
                    temp_path = parts[1]
                else:
                    # assume it was not part of string
                    temp_path = parts[0]

                parts = temp_path.split(':')
                if len(parts) == 2:
                    if self.host is None:
                        self.host = parts[0]
                    temp_path = parts[1]
                else:
                    # assume it was not part of string
                    temp_path = parts[0]

            self.remote_path = temp_path
            if not temp_path.endswith(os.sep):
                self.remote_path = temp_path + os.sep

    def _get_destination(self):
        """
        """
        destination = []
        if self.user:
            destination.append(self.user)
            destination.append('@')
        if self.host:
            destination.append(self.host)
            destination.append(':')
        # assume it exists; otherwise we will have issues
        destination.append(self.remote_path)

        return ''.join(destination)

    def _get_cmd(self, filename):
        """
        """
        # since we need to modify the command to add iteration specific
        # elements we will capture the base command into a local variable
        # must not forget to clone, stupid pass by reference!!!

        log.debug('base sync command [%s]', self._cmd)
        cmd = self._cmd[:]
        cmd.append(os.path.join(self.local_path, filename))
        cmd.append(self._get_destination())
        log.debug('file specific command [%s]', cmd)

        return cmd

    def _add_processed(self, torrent):
        self._processed.append(torrent)

    def _sync(self):
        raise NotImplementedError

    def execute(self):
        """
        Manages of execution of the requested sync implementation
        """
        self._sync()
        return self._processed


class SequentialSync(_BaseSync):
    """
    .. note::
        v1 of the sync task implementation
    """

    def __init__(self, *args, **kwargs):
        """
        :param list torrents:   Torrent instances to process
        :param list cmd:        command and options used to execute sync
        :param str local_path:  folder path of where the local files exist
        :param str remote_path: folder path of where to place remote files
        :param str host:        name of the host (ip address) to connect to
        :param str user:        name of the user to connect as
        """
        super(SequentialSync, self).__init__(*args, **kwargs)

    def _sync(self):
        for torrent in self.torrents:

            try:
                log.debug('syncing media files for torrent %s', torrent)
                media_files = helpers.get_media_files(torrent, synced=False)

                # now loop through the files we got back, if none then no
                # files were in need of syncing
                for media_file in media_files:
                    log.info('syncing new file %s', media_file.filename)
                    ProcessLogging.execute(self._get_cmd(media_file.filename),
                                           log)
                    log.info('file synced %s', media_file.filename)
                    helpers.synced_media_file(media_file)

                # after we are done processing the torrent added it the list
                # of processed torrents
                self._add_processed(torrent)

            except Exception as err:
                log.debug(
                    'torrent:[{0}] media_files:[{1}] stacktrace: {2}'.format(
                        torrent, media_files, traceback.format_exc()))
                log.info('%s was unable to process %s due to [%s]',
                         self.__class__.__name__, torrent, err)
                # TODO: need to refine this further so we know what errors
                # really happened
                helpers.set_torrent_failed(torrent, err)


class ParallelSync(_BaseSync):
    """
    .. note::
        v2 of the sync task implementation
    """

    def __init__(self, *args, **kwargs):
        """
        :param list torrents:   Torrent instances to process
        :param list cmd:        command and options used to execute sync
        :param str local_path:  folder path of where the local files exist
        :param str remote_path: folder path of where to place remote files
        :param str host:        name of the host (ip address) to connect to
        :param str user:        name of the user to connect as
        """
        super(ParallelSync, self).__init__(*args, **kwargs)

        self.mgr = manager.Manager(cfg.CONF.prsync.rsync_threads,
                                   cfg.CONF.prsync.thread_timeout,
                                   cfg.CONF.prsync.stdout_dir,
                                   cfg.CONF.prsync.stderr_dir)
        self.torrent_tasks = {}
        self.taskconfigs = {'print_out': cfg.CONF.prsync.print_out,
                            'stdout_buffer': cfg.CONF.prsync.stdout_buffer,
                            'stderr_buffer': cfg.CONF.prsync.stderr_buffer,
                            'stderr_verbose': cfg.CONF.prsync.stderr_verbose,
                            'host': self.host}

    def _add_torrent_task(self, torrent, media_file):

        if not torrent.name in self.torrent_tasks:
            self.torrent_tasks[torrent.name] = _TorrentTask(torrent,
                                                            set([]),
                                                            False)

        sync_task = task.Task(torrent.name, media_file.filename,
                              self._get_cmd(media_file.filename),
                              self.taskconfigs, self._task_complete)
        self.torrent_tasks[torrent.name].mediatasks.add(
            _MediaTask(media_file.filename, media_file, sync_task))

        self.mgr.add_task(sync_task)

    def _sync(self):

        for torrent in self.torrents:

            log.debug('syncing media files for torrent %s', torrent)
            media_files = helpers.get_media_files(torrent, synced=False)

            # now loop through the files we got back, if none then no
            # files were in need of syncing
            for media_file in media_files:
                log.trace('syncing file: %s', media_file.filename)
                self._add_torrent_task(torrent, media_file)

        # now execute the tasks
        statuses = self.mgr.run()

        if len(self.torrent_tasks) > 0:
            log.trace('Manually processing task_complete')
            for torrent_name in statuses:
                for media_name, status in statuses[torrent_name]:
                    self._task_complete(torrent_name,
                                        media_name,
                                        (status, None))
        else:
            log.debug('No statuses; probably processed via callback.')

    def _task_complete(self, torrent_name, media_name, result):

        processed_tasks = []
        if torrent_name in self.torrent_tasks:
            for media_task in self.torrent_tasks[torrent_name].mediatasks:
                if media_task.name == media_name:
                    # add to list for removal later on
                    processed_tasks.append(media_task)

                    if result[0] == 0:
                        helpers.synced_media_file(media_task.media)
                    else:
                        self.torrent_tasks[torrent_name].failed = True
                        log.debug(
                            'torrent:[{0}] media_files:[{1}] stacktrace: {2}'.format(  # noqa
                                self.torrent_tasks[torrent_name].torrent,
                                media_task.media, result))
                        log.info('%s was unable to process %s due to [%s]',
                                 self.__class__.__name__,
                                 self.torrent_tasks[torrent_name].torrent,
                                 result)
                        if (len(result) > 1 and result[1] is not None):
                            msg = result[1]
                        else:
                            msg = result[0]
                        helpers.set_torrent_failed(
                            self.torrent_tasks[torrent_name].torrent, msg)

                else:
                    continue

            if processed_tasks:
                # if we processed any of the tasks; we can now
                # safely remove them from the set.
                self.torrent_tasks[torrent_name].mediatasks.difference_update(
                    processed_tasks)

            # once the list of associated mediatasks is exhausted
            # we need to handle showing the torrent as processed
            # and then remove from the list of those being processed.
            if len(self.torrent_tasks[torrent_name].mediatasks) == 0:
                if not self.torrent_tasks[torrent_name].failed:
                    # after we are done processing the torrent added it
                    # the list of processed torrents
                    self._add_processed(
                        self.torrent_tasks[torrent_name].torrent)

                # now we need to remove the torrent from the torrent_tasks
                self.torrent_tasks.pop(torrent_name, None)

        else:
            # should not happen as we only remove torrent from list when
            # all the tasks for the torrent are complete.
            log.warn('torrent_tasks corrupted: missing torrent %s',
                     torrent_name)
