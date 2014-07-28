"""
Test cases for generating sample configs
"""

from seedbox import options
from seedbox import db
from seedbox import process
from seedbox import tasks
from seedbox.tests import test
from seedbox import torrent


class ConfigTest(test.BaseTestCase):

    def test_list_common_opts(self):
        self.assertIsNotNone(options.list_opts())

    def test_list_db_opts(self):
        self.assertIsNotNone(db.list_opts())

    def test_list_process_opts(self):
        self.assertIsNotNone(process.list_opts())

    def test_list_task_opts(self):
        self.assertIsNotNone(tasks.list_opts())

    def test_list_torrent_opts(self):
        self.assertIsNotNone(torrent.list_opts())
