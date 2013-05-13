#!/usr/bin/python

"""
Task Manager
"""
from __future__ import absolute_import, print_function
import os, sys
import logging
import lockfile as locker

from seedbox import __version__
from seedbox.lockfileext import TimeoutPIDLockFile
from seedbox import logext as logmgr
from seedbox import options as opt_loader
from seedbox import pluginmanager, processmap, taskmanager, datamanager

log = logging.getLogger('main')

def _get_default_location():
    """
    get default location for running
    """
    use_resource = None
    if sys.platform.startswith('win'):
        # On windows look in ~/seedbox as well, as explorer does not let you create a 
        # folder starting with a dot
        default_path = os.path.join(os.path.expanduser('~'), 'seedbox')
    else:
        default_path = os.path.join(os.path.expanduser('~'), '.seedbox')

    # if the user folder exists; then we'll use it if we were not provided one
    if os.path.exists(default_path):
        use_resource = default_path
    else:
        # if all else fails then we just use the current working directory
        use_resource = os.getcwd()

    return use_resource

def main():
    """
    Main program
    """

    # need to create a lock to make sure multiple instances do not start at the
    # sametime because we are running as a cron.
    filelock = os.path.join(_get_default_location(), 'seedmgr.lock')
    lock = TimeoutPIDLockFile(filelock, 10)
    try:
        with lock:
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
            datamanager.start(core_configs)
        
            # time to start processing
            taskmanager.start(core_configs)

    except locker.LockTimeout:
        # if we have managed timeout, it means there is another instance already running
        # so we will simply bow out and let the existing one still run.
        print('Unable to acquire a lock, so another process is still running. (see cron log)',
            file=sys.stderr)


if __name__ == '__main__':
    # not sure if this really works any longer due to absolute imports
    # fix it???
    main()

