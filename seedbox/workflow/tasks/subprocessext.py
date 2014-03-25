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
import subprocess
import threading


class ProcessLogging(subprocess.Popen):
    """
    Run a command as a subprocess sending output to a logger.
    """
    def __init__(self, cmd, logger):
        """
        :param list cmd:    command and options sent to subprocess to execute
        :param logging.Logger logger:   the logger to use to capture output
        """
        self._cmd = cmd
        self._logger = logger

        # delegate to parent to spawn the rsync process
        super(ProcessLogging, self).__init__(self._cmd, shell=False,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             bufsize=1,
                                             universal_newlines=True)

        # start stdout and stderr logging threads
        self.log_thread(self.stdout, self._logger.info)
        self.log_thread(self.stderr, self._logger.warn)

        self._logger.debug('Started subprocess, pid %s', self.pid)
        self._logger.debug('Command:  %s', ' '.join(self._cmd))

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
    def execute(cmd, logger):
        """
        provide a convenience method for creating creating the object and
        waiting for the results; very similar to check_call() but not at
        module level.

        :param list cmd:    command and options sent to subprocess to execute
        :param logging.Logger logger:   the logger to use to capture output
        """
        proc = ProcessLogging(cmd, logger)
        proc.complete()
