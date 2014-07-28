# Copyright 2011 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Time related utilities and helper functions.
"""

import functools
import logging

import datetime


class AfterDelta(object):
    """
    .. py:decorator:: AfterDelta
        A decorator that has state and handles checking if period of time
        (delta) has passed before executing the function. That way if you
        need to control whether a piece of code executes in a loop, the delta
        is applied before execution otherwise NOOP
    """

    # 60 seconds
    DEFAULT_DELTA = 60

    def __init__(self, method):
        self._method = method
        self.before = None

    def get_delta(self):
        """
        Retrieves the delta (period of time to wait between executions)

        .. note::
            To change the delta simply subclass and override
            this one method, and use the subclass name as the decorator

        :returns:   period of time (seconds)
        :rtype:     int
        """
        return self.DEFAULT_DELTA

    def __call__(self, *args, **kwargs):
        # if the timer has not started, then start it
        if self.before is None:
            self.before = utcnow()

        # if the delta has passed our timer then
        # reset timer and execute the method.
        if is_older_than(self.before, self.get_delta()):
            self.before = utcnow()
            return self._method(*args, **kwargs)
        # otherwise just return; noop
        else:
            return


def timed(method=None, logger=None, loglvl=None):
    """
    .. py:decorator:: timed(logger, loglvl)
        A decorator that times the execution of a method/function and logs
        using the supplied logger at the specified loglevel.


    :param method: the method being timed
    :param logging.Logger logger:   reference to logger
                                    (defaults to logger of module holding the
                                    decorated method or function)
    :param int loglvl:  a logging level from logging.LEVELS defaults to DEBUG
    """

    # if called without method, it means we have been called with
    # optional arguments, we return a decorator with optional arguments
    # filled in. Next time around we'll be decorating
    if method is None:
        return functools.partial(timed, logger=logger, loglvl=loglvl)

    # if no logger provided we will default to the module level
    # logger that is leveraged most often
    if logger is None:
        logger = logging.getLogger(method.__module__)

    # if no log level provided or it was invalid, then simply
    # set it to our default of DEBUG
    if loglvl is None or logging.getLevelName(loglvl).startswith('Level'):
        loglvl = logging.DEBUG

    # functools makes sure that we don't lose the method details
    # like method name or doc.
    @functools.wraps(method)
    def timer(*args, **kwargs):
        """
        Logs the execution time of the specified method.
        :param args: the positional inputs to the method being timed
        :param kwargs: the key-value inputs to the method being timed
        :return: output of method being timed
        """
        start = utcnow()
        result = method(*args, **kwargs)
        end = utcnow()

        logger.log(loglvl, '%s took %.4f secs', method.__name__,
                   delta_seconds(start, end))
        return result

    return timer


def nvl_date(dt, default=None):
    """
    Determines if the provided date, time, or datetime has a value, and returns
    the provided value back or the value of default (current time)

    :param dt: an instance of a date, time, or datetime
    :param default: value to return if provided dt has no value
    :return: date, time, or datetime provided or default
    :rtype: datetime
    """
    _default = default if default else utcnow()
    return dt if dt and isinstance(dt, datetime.datetime) else _default


def utcnow():
    """
    :returns:   current time from utc
    :rtype:     datetime
    """
    return datetime.datetime.utcnow()


def time_delta_seconds(seconds):
    """
    Retrieves a timedelta

    :param int seconds: delta of seconds
    :returns:   timedelta by seconds
    :rtype:     timedelta
    """
    return datetime.timedelta(seconds=seconds)


def advance_time_delta(dt, timedelta):
    """
    Advances a datetime by a datetime.timedelta

    :param datetime dt: a specified date time
    :param datetime.timedelta timedelta:    time offset (delta)
    :returns:   a datetime incremented by delta
    :rtype:     datetime
    """
    return dt + timedelta


def advance_time_seconds(dt, seconds):
    """
    Advances a datetime by a seconds

    :param datetime dt: a specified date time
    :param int seconds: seconds (delta)
    :returns:   a datetime incremented by seconds
    :rtype:     datetime
    """
    return advance_time_delta(dt, time_delta_seconds(seconds))


def is_older_than(before, seconds):
    """
    Checks if a datetime is older than seconds

    :param datetime before: a datetime to check
    :param int seconds: seconds (delta)
    :returns:   True if before is older than seconds else False
    :rtype: bool
    """
    return utcnow() - before > time_delta_seconds(seconds)


def is_newer_than(after, seconds):
    """
    Checks if a datetime is newer than seconds

    :param datetime after: a datetime to check
    :param int seconds: seconds (delta)
    :returns:   True if before is newer than seconds else False
    :rtype: bool
    """
    return after - utcnow() > time_delta_seconds(seconds)


def delta_seconds(before, after):
    """
    Return the difference between two timing objects.

    Compute the difference in seconds between two date, time, or
    datetime objects (as a float, to microsecond resolution).

    :param before:  date, datetime, time object
    :param after:   date, datetime, time object
    :returns:       difference in seconds
    :rtype:         int
    """
    delta = after - before
    return total_seconds(delta)


def total_seconds(delta):
    """
    Return the total seconds of datetime.timedelta object.

    Compute total seconds of datetime.timedelta, datetime.timedelta
    doesn't have method total_seconds in Python2.6, calculate it manually.

    :param timedelta delta: a delta to convert
    :returns:   seconds
    :rtype:     int
    """
    try:
        return delta.total_seconds()
    except AttributeError:
        return ((delta.days * 24 * 3600) + delta.seconds +
                float(delta.microseconds) / (10 ** 6))


def is_soon(dt, window):
    """
    Determines if time is going to happen in the next window seconds.

    :param dt: the time
    :param window: minimum seconds to remain to consider the time not soon

    :return: True if expiration is within the given duration
    """
    soon = advance_time_seconds(utcnow(), window)
    return dt <= soon


# Defined here such that total_seconds is properly defined prior to usage
ONE_WEEK = total_seconds(datetime.timedelta(weeks=1))
