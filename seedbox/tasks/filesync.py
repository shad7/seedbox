"""
SyncFile task plugin for performing rsync of a file to a specified location.
"""
import logging
import os

from oslo.config import cfg

from seedbox.tasks import base
from seedbox.tasks import subprocessext

LOG = logging.getLogger(__name__)

OPTS = [
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
]

cfg.CONF.register_opts(OPTS, group='tasks_filesync')


class SyncFile(base.BaseTask):
    """
    Provides the capability of rsync file to a specified location.
    """

    def __init__(self, media_file):
        super(SyncFile, self).__init__(media_file)
        self._cmd = None
        self._destination = None

    @property
    def cmd(self):
        """
        A property for accessing the rsync command used for specified media
        file.

        :return: rsync command
        :rtype: list
        """
        if self._cmd is None:
            self._cmd = ['rsync']

            if cfg.CONF.tasks_filesync.dryrun:
                self._cmd.append('--dry-run')
            if cfg.CONF.tasks_filesync.verbose:
                self._cmd.append('--verbose')
            if cfg.CONF.tasks_filesync.progress:
                self._cmd.append('--progress')
            if cfg.CONF.tasks_filesync.perms:
                self._cmd.append('--perms')
            if cfg.CONF.tasks_filesync.delayupdates:
                self._cmd.append('--delay-updates')
            if cfg.CONF.tasks_filesync.recursive:
                self._cmd.append('--recursive')
            if cfg.CONF.tasks_filesync.chmod:
                self._cmd.append('--chmod=%s' % cfg.CONF.tasks_filesync.chmod)

            if (cfg.CONF.tasks_filesync.identity or
                    cfg.CONF.tasks_filesync.port):
                ssh_cmd = '--rsh=ssh'
                if cfg.CONF.tasks_filesync.port:
                    ssh_cmd = ssh_cmd + ' -p ' + cfg.CONF.tasks_filesync.port
                if cfg.CONF.tasks_filesync.identity:
                    ssh_cmd = ssh_cmd + ' -i ' + \
                        cfg.CONF.tasks_filesync.identity

                self._cmd.append(ssh_cmd)

            self._cmd.append(os.path.join(cfg.CONF.tasks.sync_path,
                                          self.media_file.filename))
            self._cmd.append(self.destination)

        LOG.debug('formatted cmd: [%s]', self._cmd)
        return self._cmd

    @property
    def destination(self):
        """
        A property for accessing the destination to sync file to.

        :return: remote destination
        :rtype: string
        """
        if self._destination is None:
            self._destination = []
            self._destination.append(cfg.CONF.tasks_filesync.remote_user)
            self._destination.append('@')
            self._destination.append(cfg.CONF.tasks_filesync.remote_host)
            self._destination.append(':')
            self._destination.append(cfg.CONF.tasks_filesync.remote_path)

        LOG.debug('destination: [%s]', self._destination)
        return ''.join(self._destination)

    @staticmethod
    def is_actionable(media_file):
        """
        Perform check to determine if action should be taken.

        :param media_file: an instance of a MediaFile to check
        :returns: a flag indicating to act or not to act
        :rtype: boolean
        """
        return (media_file.file_path == cfg.CONF.tasks.sync_path and
                not media_file.synced)

    def execute(self):
        """
        Perform the action associated with task for the provided media_file.
        """
        LOG.debug('syncing file %s', self.media_file.filename)
        subprocessext.ProcessLogging.execute(self.cmd)
        self.media_file.synced = True
