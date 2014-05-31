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
            next_step()

        return self.is_done()
