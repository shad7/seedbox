from __future__ import absolute_import
import unittest
import os, sys

# required since we leverage custom logging levels
from seedbox import logext as logmgr

# now include what we need to test
import seedbox.options as opt_loader

__version__ = '0.1'

class TestOptions(unittest.TestCase):
    """
    Test all aspects of loading file and command line options
    and then storing and accessing them via a Namespace
    """

    def setUp(self):
        # since we execute everything via setup.py; need to determine
        # where we really are so we have the correct path for finding
        # test configuration files.
        name = os.sep.join(__name__.split('.'))
        self.mod_path = os.path.dirname(os.path.abspath(name))

    def test_init(self):
        """
        test the initliaze process
        """
        configurator = opt_loader.initialize(__version__)
        self.assertIsInstance(configurator, opt_loader.ConfigOptions)

    def test_command_line_defaults(self):
        """
        Verify the default values after processing command line
        """
        configurator = opt_loader.initialize(__version__)

        core_configs = configurator.get_configs()

        self.assertIsNone(core_configs.resource_path)
        self.assertEqual(core_configs.rcfile, opt_loader.DEFAULT_CFG_FILENAME)
        self.assertEqual(core_configs.logfile, opt_loader.DEFAULT_LOG_FILENAME)
        self.assertEqual(core_configs.loglevel, opt_loader.DEFAULT_LOG_LEVEL)
        self.assertFalse(core_configs.reset)
        self.assertFalse(core_configs.retry)
        self.assertFalse(core_configs.dev)

    def test_local_config_file(self):
        """
        Verify we load a config file stored in current working directory
        """
        configurator = opt_loader.initialize(__version__)

        core_configs = configurator.get_configs()
        # force a value in for resource_path (given it gets executed such it can't be found)
        core_configs.resource_path = self.mod_path

        configurator.load_configs()
        core_configs = configurator.get_configs()
        self.assertIsNotNone(core_configs.resource_path)

    def test_config_file_requireds(self):
        """
        Verify we have all the required values
        """
        configurator = opt_loader.initialize(__version__)

        core_configs = configurator.get_configs()
        # force a value in for resource_path (given it gets executed such it can't be found)
        core_configs.resource_path = self.mod_path

        configurator.load_configs()

        core_configs = configurator.get_configs()
        self.assertIsNotNone(core_configs.torrent_path)
        self.assertIsNotNone(core_configs.media_paths)

    def test_missing_config_file(self):
        """
        Verify that we get an exception if the configuration file is missing
        """
        configurator = opt_loader.initialize(__version__)

        core_configs = configurator.get_configs()

        # force a value in for rcfile
        core_configs.rcfile = os.path.join(self.mod_path, 'missing.cfg')
        
        with self.assertRaises(IOError):
            configurator.load_configs()

    def test_missing_file_requireds(self):
        """
        verify that an exception is raised when missing required inputs
        """
        configurator = opt_loader.initialize(__version__)

        core_configs = configurator.get_configs()

        # force a value in for rcfile
        core_configs.rcfile = os.path.join(self.mod_path, 'bad.cfg')

        with self.assertRaises(ValueError):
            configurator.load_configs()

    def test_verify_list_attributes(self):
        """
        Verify media_paths, plugin_paths, disabled_phases
        """
        configurator = opt_loader.initialize(__version__)

        core_configs = configurator.get_configs()
        # force a value in for resource_path (given it gets executed such it can't be found)
        core_configs.resource_path = self.mod_path

        configurator.load_configs()

        core_configs = configurator.get_configs()

        self.assertIsInstance(core_configs.media_paths, list)
        self.assertIsInstance(core_configs.plugin_paths, list)
        self.assertIsInstance(core_configs.disabled_phases, list)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOptions)
    unittest.TextTestRunner(verbosity=2).run(suite)

