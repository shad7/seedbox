#!/usr/bin/env python
"""
The main program that is the entry point for the SeedboxManager application.
Provides the ability to configure and start up processing.
"""
from __future__ import absolute_import
import logging
import os
import sys

import lockfile
from lockfile import pidlockfile
from oslo.config import cfg

from seedbox import db
from seedbox import logext as logmgr
from seedbox import options
from seedbox import process

LOG = logging.getLogger(__name__)


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
    cfg.CONF.log_opt_values(LOG, logging.DEBUG)

    try:
        # need to create a lock to make sure multiple instances do not start
        # at the same time because we are running as a cron.
        with pidlockfile.PIDLockFile(os.path.join(cfg.CONF.config_dir,
                                     'seedmgr.lock'), timeout=10):

            # setup database and initialize connection
            db.dbapi(cfg.CONF)

            # time to start processing
            process.start()

    except lockfile.LockTimeout as lockerr:
        # if we have managed timeout, it means there is another instance
        # already running so we will simply bow out and let the existing
        # one still run.
        LOG.info('Already running; if not delete lock file: %s', lockerr)
