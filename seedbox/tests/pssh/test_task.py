import os

import mock

from seedbox.tests import test
from seedbox.pssh import manager
from seedbox.pssh import task


def print_output(torrent, media, results):
    print 'tor=%s media=%s results=%s' % (torrent, media, results)


class Writer(object):

    def open_files(self, host):
        return host + '_out', host + '_err'

    def write(self, filename, data):
        print 'write(', filename, ':', data, ')'

    def close(self, filename):
        print 'close(', filename, ')'


class PsshTaskTest(test.BaseTestCase):

    def test_task_no_output(self):
        opts = {'print_out': False,
                'stdout_buffer': False,
                'stderr_buffer': False,
                'stderr_verbose': False,
                'host': 'localhost'
                }
        cmd = ['uname']
        _task = task.Task('torrent1', 'media1', cmd, opts, print_output)

        writer = None
        iomap = mock.Mock(spec=manager.PollIOMap())

        _task.start(iomap, writer)

        print 'task:', _task
        print 'elasped:', _task.elapsed()
        print 'running:', _task.running()
        print 'results:', _task.get_results()
        print 'report:', _task.report(1)

    def test_task_writer(self):

        opts = {'print_out': True,
                'stdout_buffer': True,
                'stderr_buffer': True,
                'stderr_verbose': True,
                'host': 'localhost'
                }
        cmd = ['ls', '-laR', os.path.expanduser('~')]
        _task = task.Task('torrent2', 'media2', cmd, opts, print_output)

        writer = Writer()
        iomap = mock.Mock(spec=manager.PollIOMap())

        _task.start(iomap, writer)

        print 'task:', _task
        print 'elasped:', _task.elapsed()
        print 'running:', _task.running()
        print 'results:', _task.get_results()
        print 'report:', _task.report(1)

    def test_task_cancel(self):

        opts = {'print_out': True,
                'stdout_buffer': True,
                'stderr_buffer': True,
                'stderr_verbose': True,
                'host': 'localhost'
                }
        cmd = ['ls', '-laR', os.path.expanduser('~')]
        _task = task.Task('torrent3', 'media3', cmd, opts, print_output)

        _task.cancel()

        print 'task:', _task
        print 'running:', _task.running()
        print 'results:', _task.get_results()
        print 'report:', _task.report(1)

    def test_task_timedout(self):

        opts = {'print_out': True,
                'stdout_buffer': True,
                'stderr_buffer': True,
                'stderr_verbose': True,
                'host': 'localhost'
                }
        cmd = ['sleep', '5']
        _task = task.Task('torrent4', 'media4', cmd, opts, print_output)

        writer = Writer()
        iomap = mock.Mock(spec=manager.PollIOMap())

        _task.start(iomap, writer)
        _task.timedout()
        _task.timedout()

        print 'task:', _task
        print 'running:', _task.running()
        print 'results:', _task.get_results()
        print 'report:', _task.report(1)

    def test_task_interrupted(self):

        opts = {'print_out': True,
                'stdout_buffer': True,
                'stderr_buffer': True,
                'stderr_verbose': True,
                'host': 'localhost'
                }
        cmd = ['sleep', '5']
        _task = task.Task('torrent5', 'media5', cmd, opts, print_output)

        writer = Writer()
        iomap = mock.Mock(spec=manager.PollIOMap())

        _task.start(iomap, writer)
        _task.interrupted()
        _task.interrupted()

        print 'task:', _task
        print 'running:', _task.running()
        print 'results:', _task.get_results()
        print 'report:', _task.report(1)

    def test_task_timedout_nostart(self):

        opts = {'print_out': True,
                'stdout_buffer': True,
                'stderr_buffer': True,
                'stderr_verbose': True,
                'host': 'localhost'
                }
        cmd = ['ls', '-laR', os.path.expanduser('~')]
        _task = task.Task('torrent6', 'media6', cmd, opts, print_output)

        _task.timedout()
        _task.timedout()

        print 'task:', _task
        print 'running:', _task.running()
        print 'results:', _task.get_results()
        print 'report:', _task.report(1)

    def test_task_interrupted_nostart(self):

        opts = {'print_out': True,
                'stdout_buffer': True,
                'stderr_buffer': True,
                'stderr_verbose': True,
                'host': 'localhost'
                }
        cmd = ['ls', '-laR', os.path.expanduser('~')]
        _task = task.Task('torrent7', 'media7', cmd, opts, print_output)

        _task.interrupted()
        _task.interrupted()

        print 'task:', _task
        print 'running:', _task.running()
        print 'results:', _task.get_results()
        print 'report:', _task.report(1)
