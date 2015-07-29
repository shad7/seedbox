from __future__ import print_function

import datetime

from seedbox.common import timeutil
from seedbox.tests import test


def advance_time_delta(dt, timedelta):
    return dt + timedelta


def advance_time_seconds(dt, seconds):
    return advance_time_delta(dt, datetime.timedelta(seconds=seconds))


class TimeutilTest(test.BaseTestCase):

    def test_is_older_than(self):
        _past = advance_time_seconds(timeutil.utcnow(), -10)
        self.assertTrue(timeutil.is_older_than(_past, 5))
        self.assertFalse(timeutil.is_older_than(_past, 15))

    def test_is_newer_than(self):
        _future = advance_time_seconds(timeutil.utcnow(), 10)
        self.assertTrue(timeutil.is_newer_than(_future, 5))
        self.assertFalse(timeutil.is_newer_than(_future, 15))

    def test_delta_seconds(self):
        _future = advance_time_seconds(timeutil.utcnow(), 10)
        self.assertTrue(timeutil.delta_seconds(timeutil.utcnow(), _future), 10)

    def test_total_seconds(self):
        secs = timeutil.total_seconds(datetime.timedelta(seconds=60))
        self.assertEqual(secs, 60)
