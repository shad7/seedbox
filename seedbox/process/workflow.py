"""
Workflow implementation that handles automatic execution of each workflow
step until the workflow reaches completion.

::

    wf = Workflow(torrent)
    tasks = wf.next_tasks()
    # execute tasks in separate threads
    <<logic>>
    # now move the workflow to the next step
    wf.run()

"""
import logging

from seedbox.process import flow

LOG = logging.getLogger(__name__)


class Workflow(flow.BaseFlow):
    """
    Wrapper class around Flow that handles the orchestration of the process
    """

    def run(self):
        """Orchestrate each step of the process based on current state"""

        if not self.is_done():
            next_step = getattr(self, self.phase)
            LOG.debug('next_step: %s', next_step)
            try:
                next_step()
            except (flow.WorkflowError, flow.AbortTransition,
                    flow.InvalidTransitionError,
                    flow.ForbiddenTransition) as wferr:
                LOG.error('workflow error: %s', wferr)
                self.torrent = self.dbapi.get_torrent(self.torrent.torrent_id)
                self.torrent.error_msg = str(wferr)
                self.torrent.failed = True
                self.torrent = self.dbapi.save_torrent(self.torrent)
                return True

        return self.is_done()
