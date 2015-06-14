"""
Constants needed throughout application.
"""

INIT = 'init'
READY = 'ready'
ACTIVE = 'active'
DONE = 'done'
CANCELLED = 'cancelled'

STATES = [INIT, READY, ACTIVE, DONE, CANCELLED]
ACTIVE_STATES = [INIT, READY, ACTIVE]
INACTIVE_STATES = [DONE, CANCELLED]
