from __future__ import absolute_import
import os
import random
import tempfile

import seedbox.db.schema as schema
import seedbox.db.api as dbapi
from seedbox.tests import test
from seedbox.workflow import helpers
from seedbox.workflow.tasks import filedelete


class FileDeleteTest(test.ConfiguredBaseTestCase):

    def setUp(self):
        super(FileDeleteTest, self).setUp()

        # initialize the database and schema details.
        schema.init()

        self.torrent = dbapi.add_torrent('add_funnny-{0}.torrent'.format(
            random.randint(1, 999999999)))

        self.medias = []
        media1 = tempfile.NamedTemporaryFile(suffix='.mp4',
                                             dir=self.CONF.plugins.sync_path,
                                             delete=False)
        self.medias.append(media1)

        media2 = tempfile.NamedTemporaryFile(suffix='.mp4',
                                             dir=self.CONF.plugins.sync_path,
                                             delete=False)
        self.medias.append(media2)

        media_files = [media1.name,
                       media2.name,
                       ]

        helpers.add_mediafiles_to_torrent(self.torrent,
                                          self.CONF.plugins.sync_path,
                                          media_files)

    def test_filedelete(self):

        files = dbapi.get_files_by_torrent(self.torrent)
        for file in files:
            helpers.synced_media_file(file)

        task = filedelete.DeleteFile()
        results = task.execute([self.torrent])

        self.assertEqual(len(results), 1)

    def test_file_already_deleted(self):

        for file in self.medias:
            os.remove(os.path.join(self.base_dir, file.name))

        files = dbapi.get_files_by_torrent(self.torrent)
        for file in files:
            helpers.synced_media_file(file)

        task = filedelete.DeleteFile()
        results = task.execute([self.torrent])

        self.assertEqual(len(results), 1)
