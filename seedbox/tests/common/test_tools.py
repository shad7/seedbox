from __future__ import absolute_import
import os

from seedbox.tests import test
# now include what we need to test
from seedbox.common import tools


class ToolsTest(test.BaseTestCase):
    """
    create a test case for each tool within tools to verify it works
    as expected.
    """

    def test_verify_path(self):
        """
        make sure it is able to verify all different path types properly
        """
        self.assertIsNotNone(tools.verify_path(os.getcwd()))
        self.assertIsNotNone(tools.verify_path(os.path.expanduser('~')))
        self.assertIsNotNone(tools.verify_path('.'))
        self.assertIsNotNone(tools.verify_path('/lib'))
        self.assertIsNone(tools.verify_path('library'))
        self.assertIsNone(tools.verify_path('missing'))
        self.assertIsNone(tools.verify_path('/to/be/found/'))
        self.assertIsNone(
            tools.verify_path(os.path.join(os.getcwd(),
                                           'junk-tmp-simple-duh.txt')))

    def test_format_file_ext(self):
        """
        make sure it is able to process the different types of
        extension lists properly
        """
        self.assertIsInstance(tools.format_file_ext([]), list)
        self.assertEqual(len(tools.format_file_ext([])), 0)
        self.assertIsInstance(tools.format_file_ext(''), list)
        self.assertEqual(len(tools.format_file_ext('')), 0)
        self.assertIsInstance(tools.format_file_ext([' ']), list)
        self.assertEqual(len(tools.format_file_ext([' '])), 0)
        self.assertIsInstance(tools.format_file_ext(None), list)
        self.assertEqual(len(tools.format_file_ext(None)), 0)
        self.assertEqual(
            len(tools.format_file_ext(['.avi', None, '.mp4', None, ''])), 2)
        self.assertEqual(len(tools.format_file_ext(['.avi', '.mp4'])), 2)
        self.assertEqual(len(tools.format_file_ext(['avi', 'mp4'])), 2)
        self.assertEqual(len(tools.format_file_ext(['avi', '.mp4'])), 2)
        self.assertEqual(len(tools.format_file_ext(['.avi', 'mp4'])), 2)

        for ext in ['.avi', '.mp4', 'avi', 'mp4']:
            ext_list = tools.format_file_ext([ext])
            self.assertEqual(len(ext_list[0]), 4)
