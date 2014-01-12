"""
When a Task is loaded by PluginManager, each action method within the
Task is turned into an Action instance as a way to hold a reference
and compare one Action to another and sort by priority.
"""
from __future__ import absolute_import
import logging

log = logging.getLogger(__name__)

_actions = {}


class Action(object):
    """
    Enapsulates an execution method from a Task with a priority for
    comparison and sorting purposes.
    """

    def __init__(self, name, method, priority):
        """
        :param str name:        a string in the format of phase.plugin_name
        :param object method:   a reference to the execution method
                                within Task
        :param int priority:    an integer number where higher number takes
                                precendence over those with lower values.
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
        return '<Action(name=%s,method=%s,priority=%s)>' % (
            self.name,
            self.method.__name__,
            self.priority)

    __repr__ = __str__

# end of Action


def add_action_handler(name, method, priority):
    """
    creates an action with associated method and priority
    """
    actions = _actions.setdefault(name, [])
    for action in actions:
        if action.method == method:
            raise Exception(
                '%s has already been registered as action under name %s' %
                (method.__name__, name))
    log.debug('registered method %s to action %s', method.__name__, name)
    action = Action(name, method, priority)
    actions.append(action)
    return action
