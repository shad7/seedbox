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


class Taskflow(xworkflows.Workflow):
    """
    Define the workflow conditions for managing torrents;
    """
    states = (
        (constants.INIT, (u"Initial state")),
        (constants.READY, (u"Ready")),
        (constants.ACTIVE, (u"Active")),
        (constants.DONE, (u"Done")),
        (constants.CANCELLED, (u"Cancelled")),
    )

    transitions = (
        ('prepare', constants.INIT, constants.READY),
        ('activate', constants.READY, constants.ACTIVE),
        ('complete', constants.ACTIVE, constants.DONE),
        ('cancel', (constants.READY, constants.ACTIVE), constants.CANCELLED),
    )

    initial_state = constants.INIT


class BaseFlow(xworkflows.WorkflowEnabled):

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
        return get_tasks(self.phase)

    @property
    def phase(self):
        return list(Taskflow.transitions.available_from(self.state))[0].name

    def is_done(self):
        return self.state.is_done or self.state.is_cancelled

    def next_tasks(self):
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
        """
        self.torrent = self.dbapi.get_torrent(self.torrent.torrent_id)
        self.torrent.state = self.state.name
        self.torrent = self.dbapi.save_torrent(self.torrent)
        LOG.debug('torrent: %s' % self.torrent)

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
    """
    mgr = named.NamedExtensionManager('seedbox.tasks',
                                      names=cfg.CONF['process'][phase],
                                      invoke_on_load=False)

    return sorted([ext.plugin for ext in mgr.extensions])
