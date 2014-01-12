"""
Test case for version module
"""
from seedbox.tests import test
from seedbox import version


class VersionTest(test.BaseTestCase):

    def test_get_versioninfo(self):
        versioninfo = version.version_info
        self.assertIsNotNone(versioninfo)
