"""
Provide a simply extension to lockfile to support a Timeout for PIDFileLock
"""
from __future__ import absolute_import
from lockfile.pidlockfile import PIDLockFile

class TimeoutPIDLockFile(PIDLockFile, object):
    """ Lockfile with default timeout, implemented as a Unix PID file.

        This uses the ``PIDLockFile`` implementation, with the
        following changes:

        * The `acquire_timeout` parameter to the initialiser will be
          used as the default `timeout` parameter for the `acquire`
          method.

        """

    def __init__(self, path, acquire_timeout=None, *args, **kwargs):
        """ Set up the parameters of a TimeoutPIDLockFile. """
        self.acquire_timeout = acquire_timeout
        super(TimeoutPIDLockFile, self).__init__(path, *args, **kwargs)

    def acquire(self, timeout=None, *args, **kwargs):
        """ Acquire the lock. """
        if timeout is None:
            timeout = self.acquire_timeout
        super(TimeoutPIDLockFile, self).acquire(timeout, *args, **kwargs)

