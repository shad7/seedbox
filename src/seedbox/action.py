"""
encapsulate an action, and the registering of actions
"""
from __future__ import absolute_import
import logging

log = logging.getLogger(__name__)

_actions = {}

class Action(object):
    """
    enapsulates a an action
    """

    def __init__(self, name, method, priority):
        """
        initialize the action
        """
        self.name = name
        self.method = method
        self.priority = priority

    def __call__(self, *args, **kwargs):
        """
        override call to leverage the registered method
        """
        return self.method(*args, **kwargs)

    def __eq__(self, other):
        """
        override eq to compare priority
        """
        return self.priority == other.priority

    def __lt__(self, other):
        """
        override lt to compare priority
        """
        return self.priority < other.priority

    def __gt__(self, other):
        """
        override gt to compare priority
        """
        return self.priority > other.priority

    def __str__(self):
        """
        override str to provide a readable view of action
        """
        return '<Action(name=%s,method=%s,priority=%s)>' % (self.name, 
            self.method.__name__, self.priority)

    __repr__ = __str__

# end of Action

def add_action_handler(name, method, priority):
    """
    creates an action with associated method and priority
    """
    actions = _actions.setdefault(name, [])
    for action in actions:
        if action.method == method:
            raise Exception('%s has already been registered as action under name %s' % (method.__name__, name))
    log.debug('registered method %s to action %s', method.__name__, name)
    action = Action(name, method, priority)
    actions.append(action)
    return action


def get_actions(name):
    """
    @UNUSED
    retrieves a list of Action based on specified name
    """
    if not name in _actions:
        raise KeyError('No such action %s' % name)
    _actions[name].sort(reverse=True)
    return _actions[name]


def exec_action(name, *args, **kwargs):
    """
    @UNUSED
    execute the associated action based on name action
    """
    log.trace('Time to execute action named: [%s]', name)
    if not name in _actions:
        return
    for action in get_actions(name):
        log.trace('Using action: [%s]', action)
        action(*args, **kwargs)
