from __future__ import absolute_import
import logging
import subprocess
import testtools

# required since we leverage custom logging levels
from seedbox import logext as logmgr

from seedbox.tests import test
# now include what we need to test
from seedbox import subprocessext


class SubprocessExtTest(test.BaseTestCase):
    """
    Test all aspects of subprocessext module and corresponding capabilities.
    """

    def setUp(self):
        """
        create a logger
        """
        super(SubprocessExtTest, self).setUp()
        logmgr.configure()
        self.logger = logging.getLogger('subproc-ext')

    def test_short_single_cmd(self):
        """
        using a single command that can be executed very quickly validate
        basic use case.
        """
        cmd = ['ls']
        subprocessext.ProcessLogging.execute(cmd, self.logger)
        # it will complete with no return value or an exception
        self.assertTrue(True)

    def test_long_single_cmd(self):
        """
        using a single command that takes atleast a few seconds to execute to
        make sure longer running commands work successfully.
        """
        cmd = ['ls', '-laR', '/lib/python2.7']
        subprocessext.ProcessLogging.execute(cmd, self.logger)
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
            subprocessext.ProcessLogging.execute(cmd, self.logger)
            # it will complete with no return value or an exception
            self.assertTrue(True)

    def test_long_multi_cmd(self):
        """
        using a list of commands that take atleast a few seconds to execute
        to demonstrate how it works subprocess is executed multiple
        in succession
        """
        for cmd in [['ls', '-laR', '/usr/lib/python2.7'],
                    ['ls', '-laR', '/bin'], ['ls', '-laR', '/dev'],
                    ['ls', '-laR', '/etc'], ['ls', '-laR', '/lib/perl5']]:
            subprocessext.ProcessLogging.execute(cmd, self.logger)
            # it will complete with no return value or an exception
            self.assertTrue(True)

    def test_bad_cmd(self):
        """
        run a single bad command to make sure exception happens properly.
        """
        cmd = ['ls', 'some_unknown_or_missing_file']
        # should result in exception because it is a bad command!!!
        with testtools.ExpectedException(subprocess.CalledProcessError):
            subprocessext.ProcessLogging.execute(cmd, self.logger)

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
                subprocessext.ProcessLogging.execute(cmd, self.logger)
                # it will complete with no return value or an exception
                self.assertTrue(True)
            else:
                # should result in exception because it is a bad command!!!
                with testtools.ExpectedException(
                        subprocess.CalledProcessError):
                    subprocessext.ProcessLogging.execute(cmd, self.logger)
