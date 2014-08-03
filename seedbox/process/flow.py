"""
Provides the definition of workflow (steps and transition),
and implementation what happens during each step by binding in the provided
plugins for each and updating the db cache after each step.
"""
import logging

from oslo.config import cfg
from stevedore import named
import xworkflows

from seedbox import constants
from seedbox import db

LOG = logging.getLogger(__name__)

OPTS = [
    cfg.ListOpt('prepare',
                default=[],
                help='name of tasks associated with prepare phase'),
    cfg.ListOpt('activate',
                default=[],
                help='name of tasks associated with activate phase'),
    cfg.ListOpt('complete',
                default=[],
                help='name of tasks associated with complete phase'),
    ]

cfg.CONF.register_opts(OPTS, group='process')

WorkflowError = xworkflows.WorkflowError
AbortTransition = xworkflows.AbortTransition
InvalidTransitionError = xworkflows.InvalidTransitionError
ForbiddenTransition = xworkflows.ForbiddenTransition


class Taskflow(xworkflows.Workflow):
    """
    Define the workflow conditions for managing torrents;
    """
    states = (
        (constants.INIT, u'Initial state'),
        (constants.READY, u'Ready'),
        (constants.ACTIVE, u'Active'),
        (constants.DONE, u'Done'),
        (constants.CANCELLED, u'Cancelled'),
    )

    transitions = (
        ('prepare', constants.INIT, constants.READY),
        ('activate', constants.READY, constants.ACTIVE),
        ('complete', constants.ACTIVE, constants.DONE),
        ('cancel', (constants.READY, constants.ACTIVE), constants.CANCELLED),
    )

    initial_state = constants.INIT


class BaseFlow(xworkflows.WorkflowEnabled):

    """
    Provides the base workflow implementation on binding plugin tasks to each
    step and determining which plugin is capable of operating on the media
    files of the specified torrent.

    :param torrent: an instance of a parsed torrent metadata
    :type torrent: :class:`~seedbox.db.models.Torrent`
    """
    state = Taskflow()

    def __init__(self, torrent):
        super(BaseFlow, self).__init__()
        self.torrent = torrent
        self.dbapi = db.dbapi()

        # if we failed in the middle of the flow last time
        # we need to start from where we left off
        if self.torrent.state != self.state.name:
            LOG.info('advancing state to %s', self.torrent.state)
            self.state = self.torrent.state

    @property
    def tasks(self):
        """
        Property for accessing the tasks associated with current workflow step
        by looking up the configured plugins.

        :return: list of tasks (:class:`~seedbox.tasks.base.BaseTask`)
        :rtype: list
        """
        return get_tasks(self.phase)

    @property
    def phase(self):
        """
        The name of current step/phase of the workflow

        :return: name of current phase
        :rtype: string
        """
        return list(Taskflow.transitions.available_from(self.state))[0].name

    def is_done(self):
        """
        Checks if the current state of workflow is either done or cancelled.

        :return: flag indicating workflow is done
        :rtype: boolean
        """
        return self.state.is_done or self.state.is_cancelled

    def next_tasks(self):
        """
        Find the list of tasks and associated media eligible for processing.

        :return: list of tasks
        :rtype: generator
        """
        LOG.debug('finding next tasks...')
        for task in self.tasks:
            LOG.debug('checking task: %s', task)
            for mf in list(self.dbapi.get_medias_by(self.torrent.torrent_id,
                                                    missing=False,
                                                    skipped=False)):
                LOG.debug('test media actionable %s', mf)
                if task.is_actionable(mf):
                    LOG.debug('task actionable for media: %s', mf)
                    yield task(mf)

    @xworkflows.on_enter_state()
    def update_state(self, *args, **kwargs):
        """
        Handles the capturing the current state of processing

        :param args: required parameter based on decorator (unused)
        :param kwargs: required parameter based on decorator (unused)
        """
        self.torrent = self.dbapi.get_torrent(self.torrent.torrent_id)
        self.torrent.state = self.state.name
        self.torrent = self.dbapi.save_torrent(self.torrent)
        LOG.debug('torrent: %s' % self.torrent)

    @xworkflows.transition_check()
    def validate(self):
        """
        Validate that the transition should proceed or not
        """
        LOG.debug('state: %s phase: %s torrent: %s',
                  self.state.name, self.phase, self.torrent)

        result = True
        for mf in list(self.dbapi.get_medias_by(self.torrent.torrent_id,
                                                missing=False,
                                                skipped=False)):
            # if any of the media files failed during processing
            # then we need to stop the workflow from continuing.
            if mf.error_msg:
                result = False
                break

        return result

    @xworkflows.transition()
    def prepare(self):
        """
        Executes all the tasks for a torrent at prepare phase
        """
        LOG.debug('executing prepare phase')

    @xworkflows.transition()
    def activate(self):
        """
        Executes all the tasks for a torrent at activate phase
        """
        LOG.debug('executing activate phase')

    @xworkflows.transition()
    def complete(self):
        """
        Executes all the tasks for a torrent at complete phase
        """
        LOG.debug('executing complete phase')


def get_tasks(phase):
    """
    Gets a list of tasks based the current phase of processing

    :param phase: the name of the current phase/step of workflow
    """
    mgr = named.NamedExtensionManager('seedbox.tasks',
                                      names=cfg.CONF['process'][phase],
                                      invoke_on_load=False)

    return [ext.plugin for ext in mgr.extensions]
