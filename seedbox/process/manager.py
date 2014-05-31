import logging

import concurrent.futures as conc_futures
from oslo.config import cfg

LOG = logging.getLogger(__name__)

mgr_opts = [
    cfg.IntOpt('max_processes',
               default=4,
               help='max processes to use for performing sync of torrents'),
]

CONF = cfg.CONF
CONF.register_opts(mgr_opts, 'process')


class TaskManager(object):

    def __init__(self):
        self.executor = conc_futures.ProcessPoolExecutor(
            CONF.process.max_processes)
        self.tasks = []

    def add_tasks(self, tasks):
        if isinstance(tasks, list):
            self.tasks.extend(tasks)
        else:
            self.tasks.append(tasks)

    def run(self):

        futures_task = [self.executor.submit(task) for task in self.tasks]
        del self.tasks[:]

        results = []
        for future in conc_futures.as_completed(futures_task):
            results.extend(future.result())

        return results

    def shutdown(self):
        self.executor.shutdown()
