"""
Extends the subprocess.Popen class to provide logging threads for stdout and
stderr of the child process such that it will log stdout through logging
module to provided logger.info() and log stderr to provided logger.warn().

Because using subprocess.PIPE for stdout and stderr with any of the convience
methods or with the wait() command has potential for buffer issue,
we leverage Popen directly with PIPE but then spawn a thread with access to
the corresponding logger function on the specific pipe. And then leverage the
poll method to wait for child process to complete. If the returncode is not 0,
then just like check_call() we will raise the CalledProcessError to be as
consistent as possible. This is done via the staticmethod execute().
Because we subclass Popen, you can simply create the instance and leverage
Popen methods for interaction if you prefer.

The intent here is to have the output send directly to the logger vs. being
buffered until the end with the communicate() method, or dealing with buffer
conflict issues like wait(). The logger can handle the different levels,
StreamHandler or even FileHandler and the corresponding subclasses to make it
more manageable.

This was derived from several different responses on stackoverflow and blogs
on this topic. After pulling them all together and doing several rounds of
testing, this was the result.
"""
import logging
import os
import subprocess
import time
import threading

from oslo.config import cfg

from seedbox import logext

LOG = logging.getLogger(__name__)

OPTS = [
    cfg.StrOpt('stdout_dir',
               default='$config_dir/sync_out',
               help='Output directory for stdout files'),
    cfg.StrOpt('stderr_dir',
               default='$config_dir/sync_err',
               help='Output directory for stderr files'),
    cfg.BoolOpt('stdout_verbose',
                default=False,
                help='Write output to stdout'),
    cfg.BoolOpt('stderr_verbose',
                default=True,
                help='Output verbose details about exceptions'),
]

cfg.CONF.register_opts(OPTS, group='tasks_synclog')


def make_file_logger(name, filepath, unique_id, enabled):

    if enabled:
        _handler = logging.FileHandler(
            os.path.join(filepath, 'sync.home.{0}'.format(unique_id)))
        _handler.setFormatter(logging.Formatter('%(message)s'))
    else:
        _handler = logext.NullHandler()

    _logger = logging.getLogger(name)
    _logger.propagate = 0
    _logger.setLevel(logging.INFO)
    _logger.addHandler(_handler)

    return _logger


class ProcessLogging(subprocess.Popen):
    """
    Run a command as a subprocess sending output to a logger.
    """

    def __init__(self, cmd):
        """
        :param list cmd: command and options sent to subprocess to execute
        """
        self._cmd = cmd

        _uid = time.time()
        self.stdout_logger = make_file_logger(
            'seedbox.tasks.subproc.stdout',
            cfg.CONF.tasks_synclog.stdout_dir,
            _uid,
            cfg.CONF.tasks_synclog.stdout_verbose)

        self.stderr_logger = make_file_logger(
            'seedbox.tasks.subproc.stderr',
            cfg.CONF.tasks_synclog.stderr_dir,
            _uid,
            cfg.CONF.tasks_synclog.stderr_verbose)

        # delegate to parent to spawn the rsync process
        super(ProcessLogging, self).__init__(self._cmd, shell=False,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             bufsize=1,
                                             universal_newlines=True)

        # start stdout and stderr logging threads
        self.log_thread(self.stdout, self.stdout_logger.info)
        self.log_thread(self.stderr, self.stderr_logger.info)

        LOG.debug('Started subprocess, pid %s', self.pid)
        LOG.debug('Command:  %s', ' '.join(self._cmd))

    def log_thread(self, pipe, log_func):
        """
        Start a thread logging output from pipe

        :param subprocess.PIPE pipe:    messaging channel
        :param ref log_func:            reference to the logging method
        """
        def log_output(out, log_func):
            """
            thread function to log subprocess output
            """
            for line in iter(out.readline, b''):
                log_func(line.rstrip('\n'))

        # start thread
        thread = threading.Thread(target=log_output, args=(pipe, log_func))
        thread.setDaemon(True)  # thread dies with the program
        thread.start()
        thread.join()

    def complete(self):
        """
        Handle all the processing of the subprocess
        """
        while self.poll() is None:
            # we can look to add in signal interruption handling
            # here in the future.
            pass
        else:
            # if we have a return code of anything other than 0;
            # we had some kind of failure so we should recognize the
            # error and handle accordingly.
            if self.returncode != 0:
                raise subprocess.CalledProcessError(self.returncode, self._cmd)

    @staticmethod
    def execute(cmd):
        """
        provide a convenience method for creating creating the object and
        waiting for the results; very similar to check_call() but not at
        module level.

        :param list cmd: command and options sent to subprocess to execute
        """
        proc = ProcessLogging(cmd)
        proc.complete()
