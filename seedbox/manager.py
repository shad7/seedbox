#!/usr/bin/env python
"""
The main program that is the entry point for the SeedboxManager application.
Provides the ability to configure and start up processing.
"""
import logging
import os
import sys

import lockfile
from lockfile import pidlockfile
from oslo.config import cfg

from seedbox import logext as logmgr
from seedbox import options
from seedbox import datamanager
from seedbox import pluginmanager
from seedbox import processmap
from seedbox import taskmanager

log = logging.getLogger('seedmgr')


def main():
    """
    Entry point for seedmgr
    """

    # processes all command-line inputs that control how we execute
    # logging, run mode, etc.; and we get a handle back to access
    # the info
    options.initialize(sys.argv[1:])

    # configure our logging
    logmgr.configure()
    cfg.CONF.log_opt_values(log, logging.DEBUG)

    # need to create a lock to make sure multiple instances do not start at
    # the sametime because we are running as a cron.
    filelock = os.path.join(cfg.CONF.config_dir, 'seedmgr.lock')
    lock = pidlockfile.PIDLockFile(filelock, timeout=10)
    try:
        with lock:

            # load up all task plugins; if no plugins load then we could have
            # a problem; and initialize the map between our process
            # and plugins providing actions
            processmap.init(pluginmanager.load_plugins())

            # setup database and initialize connection; then loads up all
            # torrents into the cache. Now we have a database and potentially
            # some torrents that need processing
            datamanager.start()

            # time to start processing
            taskmanager.start()

    except lockfile.LockTimeout as lockerr:
        # if we have managed timeout, it means there is another instance
        # already running so we will simply bow out and let the existing
        # one still run.
        log.info('Already running; if not delete lock file: %s', lockerr)


if __name__ == '__main__':
    main()
