from __future__ import absolute_import
import os
import random
import tempfile

import seedbox.db.schema as schema
import seedbox.db.api as dbapi
from seedbox.tests import test
from seedbox.workflow import helpers
from seedbox.workflow.tasks import filecopy


class FileCopyTest(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(FileCopyTest, self).setUp()

        # initialize the database and schema details.
        schema.init()

        self.torrent = dbapi.add_torrent('add_funnny-{0}.torrent'.format(
            random.randint(1, 999999999)))

        self.medias = []
        media1 = tempfile.NamedTemporaryFile(suffix='.mp4',
                                             dir=self.base_dir,
                                             delete=False)
        self.medias.append(media1)
        print media1, os.path.exists(os.path.join(self.base_dir, media1.name))
        media2 = tempfile.NamedTemporaryFile(suffix='.mp4',
                                             dir=self.base_dir,
                                             delete=False)
        self.medias.append(media2)
        print media2, os.path.exists(os.path.join(self.base_dir, media2.name))

        media_files = [media1.name,
                       media2.name,
                       ]

        helpers.add_mediafiles_to_torrent(self.torrent,
                                          self.base_dir,
                                          media_files)

    def test_filecopy(self):

        task = filecopy.CopyFile()
        results = task.execute([self.torrent])

        self.assertEqual(len(results), 1)

    def test_file_already_copied(self):

        files = dbapi.get_files_by_torrent(self.torrent)
        for file in files:
            file.file_path = self.CONF.plugins.sync_path

        task = filecopy.CopyFile()
        results = task.execute([self.torrent])

        self.assertEqual(len(results), 1)

    def test_filecopy_fail(self):

        for file in self.medias:
            os.remove(os.path.join(self.base_dir, file.name))

        task = filecopy.CopyFile()
        results = task.execute([self.torrent])

        self.assertEqual(len(results), 0)
