#!/usr/bin/python

"""
Task Manager
"""
from __future__ import absolute_import
import logging

from seedbox import __version__
from seedbox import logext as logmgr
from seedbox import options as opt_loader
from seedbox import pluginmanager, processmap, taskmanager, torrentmanager

log = logging.getLogger('main')

def main():
    """Main program
    """
    # processes all command-line inputs that control how we execute
    # logging, run mode, etc.; and we get a handle back to access the info
    configurator = opt_loader.initialize(__version__)

    # now retrieve processed information so we can do our setup
    core_configs = configurator.get_configs()

    # configure our logging
    logmgr.configure(logging.getLevelName(core_configs.loglevel.upper()),
        core_configs.logfile, core_configs.resource_path, core_configs.dev)

    # now that we have logging, we can process the config file
    # provided by the user; because core_configs is a reference to the
    # namespace (ala an object instance, it will automatically update,
    # so no need to acquire the core_configs again)
    configurator.load_configs()

    # load up all task plugins; if no plugins load then we could have a problem
    phasemap = pluginmanager.load_plugins(configurator, core_configs.plugin_paths)

    # now create a map between our pocess and plugins providing actions
    processmap.init(phasemap)

    # setup database and initialize connection; then loads up all torrents
    # into the cache. Now we have a database and potentially some torrents
    # that need processing
    torrentmanager.start(core_configs)

    # time to start processing
    taskmanager.start(core_configs)

if __name__ == '__main__':
    # not sure if this really works any longer due to absolute imports
    # fix it???
    main()

