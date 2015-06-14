from __future__ import print_function
import os

from seedbox.db import models
from seedbox.tasks import fileunrar
from seedbox.tests import test


class FakeRarfile(object):

    class RarFile(object):

        def __init__(self, rarfile):
            print('RarFile', rarfile)
            self.rarfile = rarfile

        def namelist(self):
            return ['fake1.mp4']

        def extractall(self, path):
            open(os.path.join(path, 'fake1.mp4'), 'w').close()

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            self.close()

        def close(self):
            pass


class FileUnrarTest(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(FileUnrarTest, self).setUp()

        if not os.path.exists(self.CONF.tasks.sync_path):
            os.mkdir(self.CONF.tasks.sync_path)

        self.media_file = models.MediaFile.make_empty()
        self.media_file.compressed = 1
        self.media_file.filename = 'fake_copy.rar'
        self.media_file.file_path = '/tmp'

        open(os.path.join('/tmp', 'fake_copy.rar'), 'w').close()

    def test_actionable(self):
        self.assertTrue(fileunrar.UnrarFile.is_actionable(self.media_file))

    def test_execute(self):
        task = fileunrar.UnrarFile(self.media_file)

        self.patch(fileunrar, 'rarfile', FakeRarfile)
        files = task()

        self.assertEqual(len(files), 2)
