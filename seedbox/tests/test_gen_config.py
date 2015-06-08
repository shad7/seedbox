"""Test cases for generating sample configs"""

from seedbox import options
from seedbox.tests import test


class ConfigTest(test.BaseTestCase):

    def test_list_common_opts(self):
        self.assertIsNotNone(options.list_opts())
