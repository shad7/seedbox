import tempfile

from seedbox.tests import test
from seedbox.pssh import manager
from seedbox.pssh import task


def print_output(torrent, media, results):
    print 'tor=%s media=%s results=%s' % (torrent, media, results)


def raise_exception(torrent, media, results):
    raise RuntimeError


class PsshManagerTest(test.BaseTestCase):

    def setUp(self):
        super(PsshManagerTest, self).setUp()

        self.base_dir = tempfile.gettempdir()

    def test_simple_manager(self):

        stdout_dir = self._make_dir('outstd')
        stderr_dir = self._make_dir('outerr')
        max_threads = 1
        thread_timeout = 0

        _mgr = manager.Manager(max_threads, thread_timeout,
                               stdout_dir, stderr_dir)

        opts = {'print_out': False,
                'stdout_buffer': False,
                'stderr_buffer': False,
                'stderr_verbose': False,
                'host': 'localhost'
                }
        cmd = ['uname']
        _task = task.Task('torrent1', 'media1', cmd, opts, print_output)

        _mgr.add_task(_task)

        statuses = _mgr.run()
        self.assertEqual(len(statuses), 1)

    def test_manager_no_outdirs(self):
        max_threads = 1
        thread_timeout = 0

        _mgr = manager.Manager(max_threads, thread_timeout,
                               None, None)

        opts = {'print_out': False,
                'stdout_buffer': False,
                'stderr_buffer': False,
                'stderr_verbose': False,
                'host': 'localhost'
                }
        cmd = ['uname']
        _task = task.Task('torrent1', 'media1', cmd, opts, print_output)

        _mgr.add_task(_task)

        statuses = _mgr.run()
        self.assertEqual(len(statuses), 1)

    def test_manager_no_callback(self):
        max_threads = 1
        thread_timeout = 0

        _mgr = manager.Manager(max_threads, thread_timeout,
                               None, None)

        opts = {'print_out': False,
                'stdout_buffer': False,
                'stderr_buffer': False,
                'stderr_verbose': False,
                'host': 'localhost'
                }
        cmd = ['uname']
        _task = task.Task('torrent1', 'media1', cmd, opts, None)

        _mgr.add_task(_task)

        statuses = _mgr.run()
        self.assertEqual(len(statuses), 1)

    def test_manager_callback_exception(self):
        max_threads = 1
        thread_timeout = 0

        _mgr = manager.Manager(max_threads, thread_timeout,
                               None, None)

        opts = {'print_out': False,
                'stdout_buffer': False,
                'stderr_buffer': False,
                'stderr_verbose': False,
                'host': 'localhost'
                }
        cmd = ['uname']
        _task = task.Task('torrent1', 'media1', cmd, opts, raise_exception)

        _mgr.add_task(_task)

        statuses = _mgr.run()
        self.assertEqual(len(statuses), 1)

    def test_manager_with_timeout(self):
        max_threads = 1
        thread_timeout = 2

        _mgr = manager.Manager(max_threads, thread_timeout,
                               None, None)

        opts = {'print_out': False,
                'stdout_buffer': False,
                'stderr_buffer': False,
                'stderr_verbose': False,
                'host': 'localhost'
                }
        cmd = ['sleep', '5']
        _task = task.Task('torrent1', 'media1', cmd, opts, None)

        _mgr.add_task(_task)

        statuses = _mgr.run()
        self.assertEqual(len(statuses), 1)

    def test_manager_with_no_timeout(self):
        max_threads = 1
        thread_timeout = 6

        _mgr = manager.Manager(max_threads, thread_timeout,
                               None, None)

        opts = {'print_out': False,
                'stdout_buffer': False,
                'stderr_buffer': False,
                'stderr_verbose': False,
                'host': 'localhost'
                }
        cmd = ['sleep', '5']
        _task1 = task.Task('torrent1', 'media1', cmd, opts, None)
        _task2 = task.Task('torrent2', 'media2', cmd, opts, None)

        _mgr.add_task(_task1)
        _mgr.add_task(_task2)

        statuses = _mgr.run()
        self.assertEqual(len(statuses), 2)

    def test_manager_multi_task(self):
        max_threads = 2
        thread_timeout = 0

        _mgr = manager.Manager(max_threads, thread_timeout,
                               None, None)

        opts = {'print_out': False,
                'stdout_buffer': False,
                'stderr_buffer': False,
                'stderr_verbose': False,
                'host': 'localhost'
                }
        cmd = ['sleep', '5']
        _task1 = task.Task('torrent1', 'media1', cmd, opts, None)
        _task2 = task.Task('torrent2', 'media2', cmd, opts, None)

        _mgr.add_task(_task1)
        _mgr.add_task(_task2)

        statuses = _mgr.run()
        self.assertEqual(len(statuses), 2)

    def test_manager_multi_task_stderr(self):
        max_threads = 2
        thread_timeout = 0
        stderr_dir = self._make_dir('outerr')

        _mgr = manager.Manager(max_threads, thread_timeout,
                               None, stderr_dir)

        opts = {'print_out': False,
                'stdout_buffer': False,
                'stderr_buffer': True,
                'stderr_verbose': True,
                'host': 'localhost'
                }
        cmd = ['sleep', '5']
        _task1 = task.Task('torrent1', 'media1', cmd, opts, None)
        _task2 = task.Task('torrent2', 'media2', cmd, opts, None)

        _mgr.add_task(_task1)
        _mgr.add_task(_task2)

        statuses = _mgr.run()
        self.assertEqual(len(statuses), 2)

    def test_manager_multi_task_stdout(self):
        max_threads = 2
        thread_timeout = 0
        stdout_dir = self._make_dir('outstd')

        _mgr = manager.Manager(max_threads, thread_timeout,
                               stdout_dir, None)

        opts = {'print_out': True,
                'stdout_buffer': True,
                'stderr_buffer': False,
                'stderr_verbose': False,
                'host': 'localhost'
                }
        cmd = ['sleep', '5']
        _task1 = task.Task('torrent1', 'media1', cmd, opts, None)
        _task2 = task.Task('torrent2', 'media2', cmd, opts, None)

        _mgr.add_task(_task1)
        _mgr.add_task(_task2)

        statuses = _mgr.run()
        self.assertEqual(len(statuses), 2)
