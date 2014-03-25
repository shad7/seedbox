"""
workflow
"""
from __future__ import absolute_import
import xworkflows


class Taskflow(xworkflows.Workflow):
    """
    Define the workflow conditions for managing torrents;
    """
    states = (
        ('init', (u"Initial state")),
        ('ready', (u"Ready")),
        ('active', (u"Active")),
        ('done', (u"Done")),
        ('cancelled', (u"Cancelled")),
    )

    transitions = (
        ('prepare', 'init', 'ready'),
        ('activate', 'ready', 'active'),
        ('complete', 'active', 'done'),
        ('cancel', ('ready', 'active'), 'cancelled'),
    )

    initial_state = 'init'


class BaseFlow(xworkflows.WorkflowEnabled):

    state = Taskflow()

    def __init__(self):
        super(BaseFlow, self).__init__()

    @xworkflows.transition()
    def prepare(self, torrents):
        """
        Executes all the torrents ready for processing at prepare phase

        :param list torrents:   group of Torrent to process via Tasks
        :returns:               Torrents successfully processed during
                                prepare phase
        :rtype:                 list
        """
        return self._run(torrents)

    @xworkflows.transition()
    def activate(self, torrents):
        """
        Executes all the torrents ready for processing at activate phase

        :param list torrents:   group of Torrent to process via Tasks
        :returns:               Torrents successfully processed during
                                activate phase
        :rtype:                 list
        """
        return self._run(torrents)

    @xworkflows.transition()
    def complete(self, torrents):
        """
        Executes all the torrents ready for processing at complete phase

        :param list torrents:   group of Torrent to process via Tasks
        :returns:               Torrents successfully processed during
                                complete phase
        :rtype:                 list
        """
        return self._run(torrents)

    def get_next_step(self, tran_name):
        """
        get the function we need to execute to perform transition
        if you do not name your transition methods after the name of the
        transitions then you need to find out which function maps to
        which transition. All of this information is stored within the
        workflow library xworkflows based on what we defined previously.
        I'd rather not depend on the internals especially names of things
        but it is what it is and I like automation!
        """
        imp_dict = self._xworkflows_implems.get('state')

        return imp_dict.transitions_at.get(tran_name)

    def _run(self, torrents):
        raise NotImplementedError
