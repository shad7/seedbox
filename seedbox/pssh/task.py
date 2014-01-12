# Copyright (c) 2009-2012, Andrew McNabb

from errno import EINTR
from subprocess import Popen, PIPE
import os
import signal
import sys
import time
import traceback

BUFFER_SIZE = 1 << 16

try:
    bytes
except NameError:
    bytes = str


class Task(object):
    """Starts a process and manages its input and output.

    Upon completion, the `exitstatus` attribute is set to the exit status
    of the process.
    """
    def __init__(self, torrent, media, cmd, opts, callback=None):

        # captured as 'keys' to identify which task this is
        self.torrent = torrent
        self.media = media

        self.cmd = cmd
        self.callback = callback

        self.host = opts['host']

        # Set options.
        self.verbose = opts['stderr_verbose']
        self.print_out = opts['print_out']
        self.inline = opts['stderr_buffer']
        self.inline_stdout = opts['stdout_buffer']

        self.exitstatus = None
        self.proc = None
        self.writer = None
        self.timestamp = None
        self.failures = []
        self.killed = False
        self.outputbuffer = bytes()
        self.errorbuffer = bytes()

        self.stdout = None
        self.stderr = None
        self.outfile = None
        self.errfile = None

    def __str__(self):
        """
        Create a string representation of a Task
        """
        return '{0}: {1}-{2}:{3}'.format(self.__class__.__name__,
                                         self.host,
                                         self.torrent,
                                         self.media)

    def start(self, iomap, writer):
        """Starts the process and registers files with the IOMap."""
        self.writer = writer

        if writer:
            self.outfile, self.errfile = writer.open_files(self.host)

        # Create the subprocess.  Since we carefully call set_cloexec() on
        # all open files, we specify close_fds=False.
        self.proc = Popen(self.cmd, stdout=PIPE, stderr=PIPE,
                          close_fds=False, preexec_fn=os.setsid)
        self.timestamp = time.time()
        self.stdout = self.proc.stdout
        iomap.register_read(self.stdout.fileno(), self.handle_stdout)
        self.stderr = self.proc.stderr
        iomap.register_read(self.stderr.fileno(), self.handle_stderr)

    def _kill(self):
        """Signals the process to terminate."""
        if self.proc:
            try:
                os.kill(-self.proc.pid, signal.SIGKILL)
            except OSError:
                # If the kill fails, then just assume the process is dead.
                pass
            self.killed = True

    def timedout(self):
        """Kills the process and registers a timeout error."""
        if not self.killed:
            self._kill()
            self.failures.append('Timed out')

    def interrupted(self):
        """Kills the process and registers an keyboard interrupt error."""
        if not self.killed:
            self._kill()
            self.failures.append('Interrupted')

    def cancel(self):
        """Stops a task that has not started."""
        self.failures.append('Cancelled')

    def elapsed(self):
        """Finds the time in seconds since the process was started."""
        return time.time() - self.timestamp

    def running(self):
        """Finds if the process has terminated and saves the return code."""
        if self.stdout or self.stderr:
            return True
        if self.proc:
            self.exitstatus = self.proc.poll()
            if self.exitstatus is None:
                if self.killed:
                    # Set the exitstatus to what it would be if we waited.
                    self.exitstatus = -signal.SIGKILL
                    return False
                else:
                    return True
            else:
                if self.exitstatus < 0:
                    message = 'Killed by signal %s' % (-self.exitstatus)
                    self.failures.append(message)
                elif self.exitstatus > 0:
                    message = 'Exited with error code %s' % self.exitstatus
                    self.failures.append(message)
                self.proc = None
                return False

    def handle_stdout(self, fd, iomap):
        """Called when the process's standard output is ready for reading."""
        try:
            buf = os.read(fd, BUFFER_SIZE)
            if buf:
                if self.inline_stdout:
                    self.outputbuffer += buf
                if self.outfile:
                    self.writer.write(self.outfile, buf)
                if self.print_out:
                    sys.stdout.write('%s: %s' % (self.host, buf))
                    if buf[-1] != '\n':
                        sys.stdout.write('\n')
            else:
                self.close_stdout(iomap)
        except (OSError, IOError):
            _, e, _ = sys.exc_info()
            if e.errno != EINTR:
                self.close_stdout(iomap)
                self.log_exception(e)

    def close_stdout(self, iomap):
        if self.stdout:
            iomap.unregister(self.stdout.fileno())
            self.stdout.close()
            self.stdout = None
        if self.outfile:
            self.writer.close(self.outfile)
            self.outfile = None

    def handle_stderr(self, fd, iomap):
        """Called when the process's standard error is ready for reading."""
        try:
            buf = os.read(fd, BUFFER_SIZE)
            if buf:
                if self.inline:
                    self.errorbuffer += buf
                if self.errfile:
                    self.writer.write(self.errfile, buf)
            else:
                self.close_stderr(iomap)
        except (OSError, IOError):
            _, e, _ = sys.exc_info()
            if e.errno != EINTR:
                self.close_stderr(iomap)
                self.log_exception(e)

    def close_stderr(self, iomap):
        if self.stderr:
            iomap.unregister(self.stderr.fileno())
            self.stderr.close()
            self.stderr = None
        if self.errfile:
            self.writer.close(self.errfile)
            self.errfile = None

    def log_exception(self, e):
        """Saves a record of the most recent exception for error reporting."""
        if self.verbose:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            exc = 'Exception: {0}, {1}, {2}'.format(
                exc_type, exc_value, traceback.format_tb(exc_traceback))
        else:
            exc = str(e)
        self.failures.append(exc)

    def get_results(self):
        return self.exitstatus, self.errorbuffer

    def report(self, n):
        """Pretty prints a status report after the Task completes."""
        error = ', '.join(self.failures)
        tstamp = time.asctime().split()[3]  # Current time
        progress = '[{0}]'.format(n)
        success = '[SUCCESS]'
        failure = '[FAILURE]'
        stderr = 'Stderr: '

        if self.failures:
            print(' '.join((progress, tstamp, failure, self.host, error)))
        else:
            print(' '.join((progress, tstamp, success, self.host)))

        # NOTE: The extra flushes are to ensure that the data is output in
        # the correct order with the C implementation of io.
        if self.outputbuffer:
            sys.stdout.flush()
            try:
                sys.stdout.buffer.write(self.outputbuffer)
                sys.stdout.flush()
            except AttributeError:
                sys.stdout.write(self.outputbuffer)
        if self.errorbuffer:
            sys.stdout.write(stderr)
            # Flush the TextIOWrapper before writing to the binary buffer.
            sys.stdout.flush()
            try:
                sys.stdout.buffer.write(self.errorbuffer)
            except AttributeError:
                sys.stdout.write(self.errorbuffer)
