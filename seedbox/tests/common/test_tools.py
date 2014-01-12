from __future__ import absolute_import
import os
import sys

from seedbox.tests import test
# now include what we need to test
from seedbox.common import tools


class ToolsTest(test.BaseTestCase):
    """
    create a test case for each tool within tools to verify it works
    as expected.
    """

    def test_to_bool(self):
        """
        make sure it converts everything it should to a boolean
        """

        self.assertTrue(tools.to_bool(True))
        self.assertTrue(tools.to_bool(1))
        self.assertTrue(tools.to_bool('1'))
        self.assertTrue(tools.to_bool('yes'))
        self.assertTrue(tools.to_bool('Yes'))
        self.assertTrue(tools.to_bool('YES'))
        self.assertTrue(tools.to_bool('true'))
        self.assertTrue(tools.to_bool('True'))
        self.assertTrue(tools.to_bool('TRUE'))
        self.assertTrue(tools.to_bool('on'))
        self.assertTrue(tools.to_bool('On'))
        self.assertTrue(tools.to_bool('ON'))
        self.assertTrue(tools.to_bool('other'))

        self.assertFalse(tools.to_bool(False))
        self.assertFalse(tools.to_bool(0))
        self.assertFalse(tools.to_bool('0'))
        self.assertFalse(tools.to_bool('no'))
        self.assertFalse(tools.to_bool('No'))
        self.assertFalse(tools.to_bool('NO'))
        self.assertFalse(tools.to_bool('false'))
        self.assertFalse(tools.to_bool('False'))
        self.assertFalse(tools.to_bool('FALSE'))
        self.assertFalse(tools.to_bool('off'))
        self.assertFalse(tools.to_bool('Off'))
        self.assertFalse(tools.to_bool('OFF'))
        self.assertFalse(tools.to_bool(None))

    def test_to_list(self):
        """
        make sure it converts everything it should to a list
        """
        self.assertIsInstance(tools.to_list([]), list)
        self.assertEqual(len(tools.to_list([])), 0)
        self.assertIsInstance(tools.to_list(['value']), list)
        self.assertEqual(len(tools.to_list(['value'])), 1)
        self.assertIsInstance(tools.to_list(['value1', 'value2']), list)
        self.assertEqual(len(tools.to_list(['value1', 'value2'])), 2)
        self.assertIsInstance(tools.to_list('value'), list)
        self.assertEqual(len(tools.to_list('value')), 1)
        self.assertIsInstance(tools.to_list('value1,value2,value3'), list)
        self.assertEqual(len(tools.to_list('value1,value2,value3')), 3)
        self.assertIsInstance(tools.to_list('value1, value2, value3'), list)
        self.assertEqual(len(tools.to_list('value1, value2, value3')), 3)
        self.assertIsInstance(tools.to_list('value1;value2;value3'), list)
        self.assertEqual(len(tools.to_list('value1;value2;value3')), 3)
        self.assertIsInstance(tools.to_list('value1; value2; value3'), list)
        self.assertEqual(len(tools.to_list('value1; value2; value3')), 3)
        self.assertIsInstance(tools.to_list('value1 value2 value3'), list)
        self.assertEqual(len(tools.to_list('value1 value2 value3')), 3)
        self.assertIsInstance(tools.to_list('value1  value2  value3'), list)
        self.assertEqual(len(tools.to_list('value1  value2  value3')), 3)
        self.assertIsInstance(tools.to_list(''), list)
        self.assertEqual(len(tools.to_list('')), 0)
        self.assertIsInstance(tools.to_list(None), list)
        self.assertEqual(len(tools.to_list(None)), 0)
        self.assertIsInstance(tools.to_list('value1:value2:value3'), list)
        self.assertEqual(len(tools.to_list('value1:value2:value3')), 1)
        self.assertIsInstance(
            tools.to_list('value1:value2:value3', ':'), list)
        self.assertEqual(len(tools.to_list('value1:value2:value3', ':')), 3)
        self.assertIsInstance(
            tools.to_list('value1: value2: value3', ':'), list)
        self.assertEqual(len(tools.to_list('value1: value2: value3', ':')), 3)

    def test_list_to_str(self):
        """
        make sure it converts all lists to a string
        """
        self.assertIsInstance(tools.list_to_str(['']), basestring)
        self.assertIsInstance(tools.list_to_str(['1', '2', '3']), basestring)
        self.assertIsInstance(
            tools.list_to_str('value1,value2,value3'), basestring)
        self.assertIsInstance(
            tools.list_to_str('value1, value2, value3'), basestring)

        self.assertIsNone(tools.list_to_str([]), basestring)
        self.assertIsNone(tools.list_to_str(' '), basestring)
        self.assertIsNone(tools.list_to_str('some value'), basestring)
        self.assertIsNone(tools.list_to_str(''), basestring)
        self.assertIsNone(tools.list_to_str(None), basestring)

    def test_to_int(self):
        """
        make sure it converts everything it should to an int
        """
        self.assertIsInstance(tools.to_int(0), int)
        self.assertEqual(tools.to_int(0), 0)
        self.assertIsInstance(tools.to_int(1), int)
        self.assertEqual(tools.to_int(1), 1)
        self.assertIsInstance(tools.to_int('0'), int)
        self.assertEqual(tools.to_int('0'), 0)
        self.assertIsInstance(tools.to_int('1'), int)
        self.assertEqual(tools.to_int('1'), 1)
        self.assertIsInstance(tools.to_int('10'), int)
        self.assertEqual(tools.to_int('10'), 10)
        self.assertIsInstance(tools.to_int(' 10 '), int)
        self.assertEqual(tools.to_int(' 10 '), 10)
        self.assertIsInstance(tools.to_int(' '), int)
        self.assertEqual(tools.to_int(' '), -99999)
        self.assertIsInstance(tools.to_int('other'), int)
        self.assertEqual(tools.to_int('other'), -99999)
        self.assertIsInstance(tools.to_int([]), int)
        self.assertEqual(tools.to_int([]), -99999)
        self.assertIsInstance(tools.to_int(None), int)
        self.assertEqual(tools.to_int(None), -99999)

    def test_verify_path(self):
        """
        make sure it is able to verify all different path types properly
        """
        self.assertIsNotNone(tools.verify_path(os.getcwd()))
        self.assertIsNotNone(tools.verify_path(sys.path[0]))
        self.assertIsNotNone(tools.verify_path(os.path.expanduser('~')))
        self.assertIsNotNone(tools.verify_path('.'))
        self.assertIsNotNone(tools.verify_path('/lib'))
        self.assertIsNone(tools.verify_path('library'))
        self.assertIsNone(tools.verify_path('missing'))
        self.assertIsNone(tools.verify_path('/to/be/found/'))
        self.assertIsNone(
            tools.verify_path(os.path.join(os.getcwd(),
                                           'junk-tmp-simple-duh.txt')))

    def test_get_exec_path(self):
        """
        make sure we are able to find different executables
        """
        self.assertIsNotNone(tools.get_exec_path('python'))
#       self.assertIsNotNone(tools.get_exec_path('unrar'))
        self.assertIsNotNone(tools.get_exec_path('rsync'))
        self.assertIsNotNone(tools.get_exec_path('ls'))
        self.assertIsNone(tools.get_exec_path('dummy-cmd-test-junk'))

    def test_format_file_ext(self):
        """
        make sure it is able to process the different types of
        extension lists properly
        """
        self.assertIsInstance(tools.format_file_ext([]), list)
        self.assertEqual(len(tools.format_file_ext([])), 0)
        self.assertIsInstance(tools.format_file_ext(''), list)
        self.assertEqual(len(tools.format_file_ext('')), 0)
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
