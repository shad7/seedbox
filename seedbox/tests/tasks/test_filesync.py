import os

from seedbox.db import models
from seedbox.tasks import filesync
from seedbox.tests import test


class FileSyncTest(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(FileSyncTest, self).setUp()

        if not os.path.exists(self.CONF.tasks.sync_path):
            os.mkdir(self.CONF.tasks.sync_path)

        self.media_file = models.MediaFile.make_empty()
        self.media_file.synced = 0
        self.media_file.filename = 'fake_sync.mp4'
        self.media_file.file_path = self.CONF.tasks.sync_path
        open(os.path.join(
            self.CONF.tasks.sync_path, 'fake_sync.mp4'), 'w').close()

        self.CONF.set_override('remote_user',
                               'fake_user',
                               group='tasks_filesync')
        self.CONF.set_override('remote_host',
                               'fake_host',
                               group='tasks_filesync')

        if not os.path.exists('/tmp/remote'):
            os.mkdir('/tmp/remote')
        self.CONF.set_override('remote_path',
                               '/tmp/remote',
                               group='tasks_filesync')

    def test_actionable(self):
        self.assertTrue(filesync.SyncFile.is_actionable(self.media_file))

    def test_cmd_defaults(self):
        task = filesync.SyncFile(self.media_file)
        self.assertIsNotNone(task.cmd)
        self.assertIn('rsync', task.cmd)

    def test_cmd_override(self):

        self.CONF.set_override('dryrun',
                               True,
                               group='tasks_filesync')

        self.CONF.set_override('verbose',
                               True,
                               group='tasks_filesync')

        self.CONF.set_override('progress',
                               True,
                               group='tasks_filesync')

        self.CONF.set_override('perms',
                               False,
                               group='tasks_filesync')

        self.CONF.set_override('delayupdates',
                               False,
                               group='tasks_filesync')

        self.CONF.set_override('recursive',
                               False,
                               group='tasks_filesync')

        self.CONF.set_override('chmod',
                               None,
                               group='tasks_filesync')

        self.CONF.set_override('identity',
                               '/tmp',
                               group='tasks_filesync')

        self.CONF.set_override('port',
                               None,
                               group='tasks_filesync')

        task = filesync.SyncFile(self.media_file)
        self.assertIsNotNone(task.cmd)
        self.assertIn('rsync', task.cmd)

        task._cmd = None
        self.CONF.set_override('identity',
                               None,
                               group='tasks_filesync')

        self.assertIsNotNone(task.cmd)
        self.assertIn('rsync', task.cmd)

    def test_destination(self):
        task = filesync.SyncFile(self.media_file)
        self.assertIsNotNone(task.destination)
        self.assertIn('fake_user', task.destination)

    def test_execute(self):
        task = filesync.SyncFile(self.media_file)

        class Dummy(object):
            class ProcessLogging(object):

                @staticmethod
                def execute(cmd):
                    pass

        self.patch(filesync, 'subprocessext', Dummy)
        files = task()
        print(files[0])
        self.assertTrue(files[0].synced)
