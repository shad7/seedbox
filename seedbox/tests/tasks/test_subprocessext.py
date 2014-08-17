from __future__ import absolute_import
import os
import subprocess
import testtools
from distutils.sysconfig import get_python_lib

from seedbox.tests import test
# now include what we need to test
from seedbox.tasks import subprocessext


class SubprocessExtTest(test.ConfiguredBaseTestCase):
    """
    Test all aspects of subprocessext module and corresponding capabilities.
    """

    def setUp(self):
        """
        create a logger
        """
        super(SubprocessExtTest, self).setUp()
        self.CONF.set_override('stdout_dir',
                               self.CONF.tasks_synclog.stdout_dir,
                               group='tasks_synclog')
        self.CONF.set_override('stderr_dir',
                               self.CONF.tasks_synclog.stderr_dir,
                               group='tasks_synclog')

        if not os.path.exists(self.CONF.tasks_synclog.stdout_dir):
            os.mkdir(self.CONF.tasks_synclog.stdout_dir)
        if not os.path.exists(self.CONF.tasks_synclog.stderr_dir):
            os.mkdir(self.CONF.tasks_synclog.stderr_dir)
        self.py_lib = os.path.abspath(os.path.join(get_python_lib(), '..'))

    def test_short_single_cmd(self):
        """
        using a single command that can be executed very quickly validate
        basic use case.
        """
        self.CONF.set_override('stdout_verbose', True, group='tasks_synclog')
        self.CONF.set_override('stderr_verbose', True, group='tasks_synclog')

        cmd = ['ls']
        subprocessext.ProcessLogging.execute(cmd)
        # it will complete with no return value or an exception
        self.assertTrue(True)

    def test_long_single_cmd(self):
        """
        using a single command that takes at least a few seconds to execute to
        make sure longer running commands work successfully.
        """
        cmd = ['ls', '-laR', self.py_lib]
        subprocessext.ProcessLogging.execute(cmd)
        # it will complete with no return value or an exception
        self.assertTrue(True)

    def test_short_multi_cmd(self):
        """
        using a list of commands that can be executed very quickly to
        demonstrate how it works subprocess is executed multiple in
        quick succession
        """
        for cmd in [['ls'], ['ls', '--help'], ['tail', '--help'],
                    ['ps', '--help'], ['mv', '--help']]:
            subprocessext.ProcessLogging.execute(cmd)
            # it will complete with no return value or an exception
            self.assertTrue(True)

    def test_long_multi_cmd(self):
        """
        using a list of commands that take at least a few seconds to execute
        to demonstrate how it works subprocess is executed multiple
        in succession
        """
        for cmd in [['ls', '-laR', self.py_lib],
                    ['ls', '-laR', os.path.expanduser('~')]]:
            subprocessext.ProcessLogging.execute(cmd)
            # it will complete with no return value or an exception
            self.assertTrue(True)

    def test_bad_cmd(self):
        """
        run a single bad command to make sure exception happens properly.
        """
        cmd = ['ls', 'some_unknown_or_missing_file']
        # should result in exception because it is a bad command!!!
        with testtools.ExpectedException(subprocess.CalledProcessError):
            subprocessext.ProcessLogging.execute(cmd)

    def test_multi_good_bad_cmd(self):
        """
        run multiple commands mixed with good and bad commands to make sure
        we can continue even if one command is bad.
        """
        for cmd in [['ls', 'some_unknown_or_missing_file'], ['ls', '--help'],
                    ['ls', 'another_unknown_or_missing_file'],
                    ['ps', '--help'],
                    ['ls', 'and_another_unknown_or_missing_file']]:
            if '--help' in cmd:
                subprocessext.ProcessLogging.execute(cmd)
                # it will complete with no return value or an exception
                self.assertTrue(True)
            else:
                # should result in exception because it is a bad command!!!
                with testtools.ExpectedException(
                        subprocess.CalledProcessError):
                    subprocessext.ProcessLogging.execute(cmd)
