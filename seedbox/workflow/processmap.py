"""
Handles mapping
"""
from __future__ import absolute_import
from collections import namedtuple
import logging

try:
    from collections import OrderedDict
except ImportError:
    # to support python < 2.7
    from ordereddict import OrderedDict

from seedbox.workflow import _workflow

log = logging.getLogger(__name__)

# leverage namedtuple to hold ordered list with named attributes for
# simple and effective access while using lease amount of memory
_TaskInfo = namedtuple('TaskInfo', ['task', 'action'])
_Phase = namedtuple('Phase', ['name', 'tasks'])

# initialize the map to an empty ordered dictionary
# order will be important
_procmap = OrderedDict()

_phasemap = OrderedDict()

# using our defined Workflow and the related transistions/phases
# generate a list of phases (in order: see tuple)
# based on existing configuration we will remove the last item which
# is the cancel phase which is not runnable ;-)
_run_phases = tuple(
    [tran.name for tran in _workflow.Taskflow.transitions][:-1])

# could use a function, but to avoid creating new variables over and over
# again just to access a name value of a state for a specified phase seemed
# overkill, so using a lambda. Provides a simple mapping of phase to state.
# based on configuration we know it is always only one related state
_phase_to_state = lambda phase: (
    _workflow.Taskflow.transitions[phase]).source[0].name

_state_to_phase = lambda state: list(
    _workflow.Taskflow.transitions.available_from(state))[0].name


def get_tasks(state):
    """
    Retrieve all tasks for a given state.

    :param str state:   A state value ['init', 'ready', 'active', 'done']
    :return:            TaskInfo (named tuple): task, action
    :rtype:             tuple of TaskInfo
    """
    return _procmap[state]


def get_state(phase):
    """
    Retrieve state for a phase

    :param str phase:   A phase value ['prepare', 'activate', 'complete']
    :return:            A state value ['init', 'ready', 'active', 'done']
    :rtype:             str
    """
    return _phase_to_state(phase)


def get_phase(state):
    """
    Retrieve phase for a state

    :param str state:   A state value ['init', 'ready', 'active', 'done']
    :return:            A phase value ['prepare', 'activate', 'complete']
    :rtype:             str
    """
    return _state_to_phase(state)


def get_run_phases():
    """
    Retrieves a list of run phases (ie those phases where execution
    can/will occur)

    :returns:   phase names ['prepare', 'activate', 'complete']
    :rtype:     ordered tuple
    """
    return _run_phases


def make_phasemap(phase, plugins):
    _phasemap[phase] = plugins


def init():
    """
    initializes the process map that links phases and states to Tasks
    """
    assert len(_phasemap) > 0, 'Plugins not loaded by phase!'

    for phase in _phasemap.keys():
        task_list = []
        for task in sorted(_phasemap[phase],
                           key=lambda plug: plug.phase_handlers[phase],
                           reverse=True):
            task_list.append(_TaskInfo(task,
                                       task.phase_handlers[phase]))

        _procmap[_phase_to_state(phase)] = _Phase(phase, tuple(task_list))

    log.trace('proc_map = %s', _procmap)
