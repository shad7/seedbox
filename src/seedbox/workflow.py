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
