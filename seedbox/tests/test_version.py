"""
Test case for version module
"""
from seedbox.tests import test
from seedbox import version


class VersionTest(test.BaseTestCase):

    def test_get_versioninfo(self):
        versioninfo = version.version_info
        self.assertIsNotNone(versioninfo)

    def test_version_str(self):
        self.assertIsNotNone(version.version_string())

    def test_release_str(self):
        self.assertIsNotNone(version.release_string())
