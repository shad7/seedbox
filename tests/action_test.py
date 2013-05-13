from __future__ import absolute_import, print_function
import unittest

# required since we leverage custom logging levels
from seedbox import logext as logmgr

# now include what we need to test
from seedbox import action

def dummy_func(*args, **kwargs):
    """
    simple dummy function to handle printing
    """
    print(args, kwargs)
    return True

def other_dummy_func(*args, **kwargs):
    """
    simple dummy function to handle printing
    """
    print(args, kwargs)
    return True


class TestAction(unittest.TestCase):
    """
    create a test case for Action to verify it works
    as expected.
    """

    def setUp(self):
        """
        create an action method that works
        """
        self.function = dummy_func
        self.other_function = other_dummy_func

    def test_add_action_handler(self):
        """
        execute add_action_handler
        """
        # need to make sure the internal dict holding registered actions is empty
        # otherwise we could end up with unexpected results
        action._actions.clear()

        self.assertIsInstance(action.add_action_handler('act1', self.function, 1), action.Action)
        self.assertIsInstance(action.add_action_handler('act2', self.function, 2), action.Action)
        self.assertIsInstance(action.add_action_handler('act3', self.function, 3), action.Action)
        self.assertIsInstance(action.add_action_handler('act77', self.function, 77), action.Action)
        self.assertIsInstance(action.add_action_handler('act71', self.function, 1), action.Action)

        # already registered this method under the same name; so it better generate
        # an Exception. Probably should be a better exception than the generic one
        with self.assertRaises(Exception):
            action.add_action_handler('act1', self.function, 1)

        # same name and priority but different function; should not generate exception
        self.assertIsInstance(action.add_action_handler('act1', self.other_function, 1), action.Action)

    def test_get_actions(self):
        """
        execute get_actions
        """
        # need to make sure the internal dict holding registered actions is empty
        # otherwise we could end up with unexpected results
        action._actions.clear()

        self.assertIsInstance(action.add_action_handler('act1', self.function, 1), action.Action)
        self.assertIsInstance(action.add_action_handler('act2', self.function, 2), action.Action)
        self.assertIsInstance(action.add_action_handler('act3', self.function, 3), action.Action)
        self.assertIsInstance(action.add_action_handler('act77', self.function, 77), action.Action)
        self.assertIsInstance(action.add_action_handler('act71', self.function, 1), action.Action)
        self.assertIsInstance(action.add_action_handler('act1', self.other_function, 1), action.Action)

        self.assertIsInstance(action.get_actions('act2'), list)
        self.assertIsInstance(action.get_actions('act3'), list)
        self.assertIsInstance(action.get_actions('act77'), list)

        self.assertEqual(len(action.get_actions('act2')), 1)
        self.assertEqual(len(action.get_actions('act3')), 1)
        self.assertEqual(len(action.get_actions('act77')), 1)
        self.assertEqual(len(action.get_actions('act71')), 1)
        self.assertEqual(len(action.get_actions('act1')), 2)

        with self.assertRaises(KeyError):
            action.get_actions('actXXXX')

    def test_exec_action(self):
        """
        execute exec_action
        """
        # need to make sure the internal dict holding registered actions is empty
        # otherwise we could end up with unexpected results
        action._actions.clear()

        self.assertIsInstance(action.add_action_handler('act1', self.function, 1), action.Action)
        self.assertIsInstance(action.add_action_handler('act2', self.function, 2), action.Action)
        self.assertIsInstance(action.add_action_handler('act3', self.function, 3), action.Action)
        self.assertIsInstance(action.add_action_handler('act77', self.function, 77), action.Action)
        self.assertIsInstance(action.add_action_handler('act71', self.function, 1), action.Action)
        self.assertIsInstance(action.add_action_handler('act1', self.other_function, 1), action.Action)

        with self.assertRaises(KeyError):
            action.exec_action('actXXXX', 0, param1=6, param2=7, param3=8)

        # our dummy functions always return True unless there is an issue
        self.assertIsNone(action.exec_action('act1', 1, param1=1, param2=2, param3=3))
        self.assertIsNone(action.exec_action('act2', 2, param1=2, param2=3, param3=4))
        self.assertIsNone(action.exec_action('act3', 3, param1=3, param2=4, param3=5))
        self.assertIsNone(action.exec_action('act77', 77, param1=4, param2=5, param3=6))
        self.assertIsNone(action.exec_action('act1', 71, param1=5, param2=6, param3=7))

    def test_action_klass(self):
        """
        test Action class and corresponding methods
        """
        action1 = action.Action('act1', self.function, 1)
        self.assertIsInstance(action1, action.Action)
        # print has no return value so it will implicitly result in None
        # this handles the test of __str__ and __repr__
        self.assertIsNone(print(action1))

        action2 = action.Action('act2', self.function, 2)
        self.assertIsInstance(action2, action.Action)
        # print has no return value so it will implicitly result in None
        # this handles the test of __str__ and __repr__
        self.assertIsNone(print(action2))

        action3 = action.Action('act3', self.function, 3)
        self.assertIsInstance(action3, action.Action)
        # print has no return value so it will implicitly result in None
        # this handles the test of __str__ and __repr__
        self.assertIsNone(print(action3))

        action77 = action.Action('act77', self.function, 77)
        self.assertIsInstance(action77, action.Action)
        # print has no return value so it will implicitly result in None
        # this handles the test of __str__ and __repr__
        self.assertIsNone(print(action77))

        action71 = action.Action('act71', self.function, 1)
        self.assertIsInstance(action71, action.Action)
        # print has no return value so it will implicitly result in None
        # this handles the test of __str__ and __repr__
        self.assertIsNone(print(action71))

        # test equal
        self.assertEqual(action1, action71)

        # test not equal
        self.assertNotEqual(action2, action3)

        # test greater than
        self.assertGreater(action77, action71)

        # test less than
        self.assertLess(action71, action2)

        # call/execute
        self.assertTrue(action1(1, param1=1, param2=2, param3=3))
        self.assertTrue(action2(2, param1=2, param2=3, param3=4))
        self.assertTrue(action3(3, param1=3, param2=4, param3=5))
        self.assertTrue(action77(77, param1=4, param2=5, param3=6))
        self.assertTrue(action71(71, param1=5, param2=6, param3=7))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAction)
    unittest.TextTestRunner(verbosity=2).run(suite)
