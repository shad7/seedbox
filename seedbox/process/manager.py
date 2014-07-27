"""
Manages the execution of tasks using parallel processes.
"""
import logging

import concurrent.futures as conc_futures
from oslo.config import cfg

LOG = logging.getLogger(__name__)

OPTS = [
    cfg.IntOpt('max_processes',
               default=4,
               help='max processes to use for performing sync of torrents'),
]

CONF = cfg.CONF
CONF.register_opts(OPTS, 'process')


class TaskManager(object):

    """
    Creates a pool of processes and executes the supplied tasks using the
    process pool.
    """

    def __init__(self):
        self.executor = conc_futures.ProcessPoolExecutor(
            CONF.process.max_processes)
        self.tasks = []

    def add_tasks(self, tasks):
        """
        Adds tasks to list of tasks to be executed.

        :param tasks: a task or list of tasks to add to the list of tasks to
                      execute
        """
        if isinstance(tasks, list):
            self.tasks.extend(tasks)
        else:
            self.tasks.append(tasks)

    def run(self):

        """
        Executes the list of tasks.

        :return: the result/output from each tasks
        :rtype: list
        """
        futures_task = [self.executor.submit(task) for task in self.tasks]
        del self.tasks[:]

        results = []
        for future in conc_futures.as_completed(futures_task):
            results.extend(future.result())

        return results

    def shutdown(self):
        """
        Shuts down the process pool to free up resources.
        """
        self.executor.shutdown()
