import logging

from seedbox.tests import test
from seedbox import logext


class LogextTest(test.ConfiguredBaseTestCase):

    def test_configure(self):
        logext.configure()
        self.assertEqual(logging.getLogger('xworkflows').getEffectiveLevel(),
                         logging.ERROR)
