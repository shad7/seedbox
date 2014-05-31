import os

from seedbox.db import models
from seedbox.tests import test
from seedbox.tasks import filedelete


class FileDeleteTest(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(FileDeleteTest, self).setUp()

        if not os.path.exists(self.CONF.tasks.sync_path):
            os.mkdir(self.CONF.tasks.sync_path)

        self.media_file = models.MediaFile.make_empty()
        self.media_file.synced = 1
        self.media_file.filename = 'fake_copy.mp4'
        self.media_file.file_path = self.CONF.tasks.sync_path

        open(os.path.join(self.CONF.tasks.sync_path,
                          'fake_copy.mp4'), 'w').close()

    def test_actionable(self):
        self.assertTrue(filedelete.DeleteFile.is_actionable(self.media_file))

    def test_execute(self):
        task = filedelete.DeleteFile(self.media_file)

        task()
        self.assertFalse(os.path.exists(
            os.path.join(self.CONF.tasks.sync_path, 'fake_copy.mp4')))
