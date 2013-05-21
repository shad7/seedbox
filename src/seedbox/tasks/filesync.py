"""
filesync was inspired by a posting for doing something similar
@ http://filesharingtalk.com/threads/436669-One-way-syncing-downloads-from-seedbox-to-home

The filesync module encapsulates the rsync command for doing a sync between
source and destination. Also tracking what has been sync'd given the nature of
seedboxes where things stay for extended periods but the destination files
are usually moved into media libraries. 

Provided is the ability to set a subset of the rsync options based on the
most common needs. Flags will be either True/False (None not supported)

    dryrun (rsync: dry-run): default[False]
    verbose: default[False]
    progress: default[False]
    perms: default[True]
    delayupdates (rsync: delay-updates): default[True]
    recursive: default[True]
    chmod: default[ugo+rwx]
    identity (rsync: rsh=ssh) default[]
    port (rsync: rsh=ssh) default[] rsyc default[22]

* assumes settings is a key:value (dict) of the possible configurations.     
"""
from __future__ import absolute_import
import logging
import os
import traceback

from seedbox import helpers
from seedbox.pluginmanager import register_plugin, phase
from seedbox.subprocessext import ProcessLogging

__version__ = '0.1'

log = logging.getLogger(__name__)

class SyncFile(object):
    """Encapsulates the rsync command with the additional feature of having a
    database cache to track which files were already successfully processed
    so they are not re-processed on future executions when the destination
    copy of the file has been moved or deleted.

    Provided is a subset of the inputs the rsync command actually supports
    but these are the most common ones required.

    dryrun (rsync: dry-run)
    verbose
    progress
    perms
    delayupdates (rsync: delay-updates)
    recursive
    chmod
    logfile (rsync: log-file)
    identity (rsync: rsh=ssh)
    port (rsync: rsh=ssh)
    """
    def __init__(self):
        """
        Establish instance variables that can be updated via configure() method
        at a later point
        """
        self._cmd = None
        self.attrs = {
            'dryrun': False,
            'verbose': False,
            'progress': False,
            'perms': True,
            'delayupdates': True,
            'recursive': True,
            'chmod': None,
            'identity': None,
            'port': None,
            'sync_path': None,
            'remote_path': None,
        }

    @phase(name='activate')
    def execute(self, torrents, configs):
        """
        perform the rsync of a file
        """
        processed_torrents = []

        log.trace('starting sync file plugin')
        self._configure(configs)

        for torrent in torrents:

            try:
                log.debug('syncing media files for torrent %s', torrent)
                media_files = helpers.get_media_files(torrent, synced=False)
    
                # now loop through the files we got back, if none then no files
                # were in need of syncing
                for media_file in media_files:
                    log.trace('syncing file: %s', media_file.filename)
                    self._sync(media_file.filename)
                    helpers.synced_media_file(media_file)
                
                # after we are done processing the torrent added it the list of
                # processed torrents
                processed_torrents.append(torrent)

            except Exception as err:
                log.debug('torrent: [{0}] media_files: [{1}] stacktrace: {2}'.format(torrent,
                    media_files, traceback.format_exc()))
                log.info('%s was unable to process %s due to [%s]', SyncFile.__name__, torrent, err)
                # TODO: need to refine this further so we know what errors really happened
                helpers.set_torrent_failed(torrent, err)

        log.trace('ending sync file plugin')
        return processed_torrents


    def _set_cmd(self):
        """Generate the rsync command using the instance variables as
        configured by user input or using the defaults we set. 

        Args:
            N/A

        Returns:
            N/A
        """
        self._cmd = ['rsync']

        if self.attrs.get('dryrun'):
            self._cmd.append('--dry-run')
        if self.attrs.get('verbose'):
            self._cmd.append('--verbose')
        if self.attrs.get('progress'):
            self._cmd.append('--progress')
        if self.attrs.get('perms'):
            self._cmd.append('--perms')
        if self.attrs.get('delayupdates'):
            self._cmd.append('--delay-updates')
        if self.attrs.get('recursive'):
            self._cmd.append('--recursive')
        if self.attrs.get('chmod'):
            self._cmd.append('--chmod=%s' % self.attrs.get('chmod'))

        if self.attrs.get('identity') or self.attrs.get('port'):
            ssh_cmd = '--rsh=ssh'
            if self.attrs.get('port'):
                ssh_cmd = ssh_cmd + ' -p ' + self.attrs.get('port')
            if self.attrs.get('identity'):
                ssh_cmd = ssh_cmd + ' -i ' + self.attrs.get('identity')

            self._cmd.append(ssh_cmd)

        log.debug('formatted cmd: [%s]', self._cmd)


    def _configure(self, configs):
        """Settings all the instance variables based on inputs provided
        by the caller. Given there is such a large number and it could
        grow over time, we support key:value pair (dict) input style.
        All flags require an input of True/False, None not allowed.

        Args:
            kwargs: key:value pair inputs for the support instance variables

        Return:
            N/A
        """
        
        # it doesn't mean any values will be actually change just most likely
        for attr_key in self.attrs.keys():
            log.trace('checking key: %s', attr_key)
            if hasattr(configs, attr_key):
                log.trace('key found in config: %s', attr_key)
                config_val = getattr(configs, attr_key)
                log.trace('value from config: %s', config_val)
                if config_val is not None:
                    log.trace('value from config is not None; setting as our attr')
                    self.attrs[attr_key] = config_val

        # now update cmd based on updated configurations
        self._set_cmd()


    def _sync(self, filename):
        """Performs actual rsync between 2 locations.

        Args:
            source_dir: source directory containing files to sync
            destination_dir: destination directory where files will be synced

        Returns:
            N/A
        """
        # Sync the file.
        log.info('syncing new file %s', filename)
        log.debug('base sync command [%s]', self._cmd)

        # since we need to modify the command to add iteration specific
        # elements we will capture the base command into a local variable
        # must not forget to clone, stupid pass by reference!!!
        cmd = self._cmd[:]

        cmd.append(os.path.join(self.attrs.get('sync_path'), filename))
        cmd.append(self.attrs.get('remote_path') + os.sep)
        log.debug('file specific command [%s]', cmd)

        ProcessLogging.execute(cmd, log)
        log.info('file synced %s', filename)


register_plugin(SyncFile)

