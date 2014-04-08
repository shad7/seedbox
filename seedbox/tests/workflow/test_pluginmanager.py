from __future__ import absolute_import

import testtools

from seedbox.tests import test
from seedbox.workflow import pluginmanager as pmgr


class DummyPlugin(object):

    disabled = False

    @pmgr.phase(name='activate')
    def test():
        pass

pmgr.register_plugin(DummyPlugin)


class DisabledPlugin(object):

    disabled = True

    @pmgr.phase(name='activate')
    def test():
        pass


class InvalidPluginA(object):

    disabled = False

    @pmgr.phase(name=' ')
    def test():
        pass


class InvalidPluginB(object):

    disabled = False

    @pmgr.phase(name='activate', priority=[9])
    def test():
        pass


class InvalidPluginC(object):

    disabled = False

    @pmgr.phase(name='')
    def test():
        pass


class InvalidPluginD(object):

    disabled = False

    def test():
        pass


class PluginManagerTest(test.ConfiguredBaseTestCase):

    def test_load_plugins(self):

        pmgr.load_plugins()
        self.assertEqual(len(list(pmgr.get_plugins())), 8)

        plugins = list(pmgr.get_plugins('complete'))
        self.assertIsNotNone(plugins)
        for p in plugins:
            print p
            print p.name

        self.CONF.set_override('copy_file_v1_disabled',
                               True,
                               group='plugins')
        pmgr.load_plugins()

    def test_duplicate_plugin(self):
        dupe_count = pmgr.PluginInfo.dupe_counter
        pmgr.register_plugin(DummyPlugin)
        self.assertNotEqual(dupe_count, pmgr.PluginInfo.dupe_counter)
        self.assertTrue(pmgr.PluginInfo.dupe_counter > dupe_count)

    def test_disabled_plugin(self):

        with testtools.ExpectedException(pmgr.DisabledPluginError):
            pmgr.register_plugin(DisabledPlugin)

    def test_invalid_plugins(self):

        with testtools.ExpectedException(pmgr.PluginError):
            pmgr.register_plugin(InvalidPluginA)

        with testtools.ExpectedException(pmgr.PluginError):
            pmgr.register_plugin(InvalidPluginB)

        with testtools.ExpectedException(pmgr.PluginError):
            pmgr.register_plugin(InvalidPluginC)

        with testtools.ExpectedException(pmgr.PluginError):
            pmgr.register_plugin(InvalidPluginD)
