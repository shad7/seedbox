"""cli program

The main program that is the entry point for the SeedboxManager application.
Provides the ability to configure and start up processing.
"""
import os
import tempfile

import lockfile

from seedbox import process
from seedbox import service


@lockfile.locked(os.path.join(tempfile.gettempdir(), __package__), timeout=10)
def main():
    """Entry point for seedmgr"""

    # processes all command-line inputs that control how we execute
    # logging, run mode, etc.; and we get a handle back to access
    # the info
    service.prepare_service()

    # time to start processing
    process.start()
