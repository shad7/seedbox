#!/usr/bin/env python
"""
The main program that is the entry point for the SeedboxManager application.
Provides the ability to configure and start up processing.
"""
from __future__ import absolute_import, print_function
import os
import sys
import logging
import lockfile
from lockfile.pidlockfile import PIDLockFile
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

    # need to create a lock to make sure multiple instances do not start at
    # the sametime because we are running as a cron.
    filelock = os.path.join(cfg.CONF.config_dir, 'seedmgr.lock')
    lock = PIDLockFile(filelock, timeout=10)
    try:
        with lock:

            # configure our logging
            logmgr.configure()

            cfg.CONF.log_opt_values(log, logging.DEBUG)

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
        print(
            'Already running; if not delete lock file: {0}'.format(lockerr),
            file=sys.stderr)


if __name__ == '__main__':
    main()
