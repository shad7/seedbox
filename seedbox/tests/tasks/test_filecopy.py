import os

from seedbox.db import models
from seedbox.tasks import filecopy
from seedbox.tests import test


class FileCopyTest(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(FileCopyTest, self).setUp()

        if not os.path.exists(self.CONF.tasks.sync_path):
            os.mkdir(self.CONF.tasks.sync_path)

        self.media_file = models.MediaFile.make_empty()
        self.media_file.compressed = 0
        self.media_file.filename = 'fake_copy.mp4'
        self.media_file.file_path = '/tmp'

        open(os.path.join('/tmp', 'fake_copy.mp4'), 'w').close()

    def test_actionable(self):
        self.assertTrue(filecopy.CopyFile.is_actionable(self.media_file))

    def test_execute(self):
        task = filecopy.CopyFile(self.media_file)

        files = task()
        self.assertEqual(files[0].file_path, self.CONF.tasks.sync_path)
