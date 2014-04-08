from __future__ import absolute_import
import testtools

from seedbox.tests import test
from seedbox.workflow import _workflow as wfdef
from seedbox.workflow import processmap


class _Plugin(object):

    def __init__(self, phase, action):
        self.phase_handlers = {}
        self.phase_handlers[phase] = action


class _Action(object):
    pass


class ProcessMapTest(test.BaseTestCase):

    PHASES = ['prepare', 'activate', 'complete']
    PLUGINS = [[_Plugin('prepare', _Action()),
                _Plugin('prepare', _Action())],
               [_Plugin('activate', _Action()),
                _Plugin('activate', _Action())],
               [_Plugin('complete', _Action()),
                _Plugin('complete', _Action())]
               ]

    def _create_phasemap(self):

        for i, phase in enumerate(self.PHASES):
            processmap.make_phasemap(phase, self.PLUGINS[i])

    def test_init(self):

        with testtools.ExpectedException(AssertionError):
            processmap.init()

        self.assertEqual(len(processmap._procmap), 0)
        self._create_phasemap()
        processmap.init()
        self.assertEqual(len(processmap._procmap), 3)

    def test_phase_and_state_mappings(self):

        run_phases = processmap.get_run_phases()
        self.assertEqual(len(run_phases), 3)

        state = processmap.get_state('prepare')
        self.assertIn(state, ['init', 'ready'])

        phase = processmap.get_phase(wfdef.Taskflow.states.init)
        self.assertEqual(phase, 'prepare')

        self._create_phasemap()
        processmap.init()
        tasks = processmap.get_tasks(wfdef.Taskflow.states.init.name)
        self.assertEqual(len(tasks), 2)
