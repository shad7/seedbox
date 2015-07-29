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

"""Time related utilities and helper functions."""

import datetime


def utcnow():
    """Gets current time.

    :returns:   current time from utc
    :rtype:     datetime
    """
    return datetime.datetime.utcnow()


def is_older_than(before, seconds):
    """Checks if a datetime is older than seconds

    :param datetime before: a datetime to check
    :param int seconds: seconds (delta)
    :returns:   True if before is older than seconds else False
    :rtype: bool
    """
    return utcnow() - before > datetime.timedelta(seconds=seconds)


def is_newer_than(after, seconds):
    """Checks if a datetime is newer than seconds

    :param datetime after: a datetime to check
    :param int seconds: seconds (delta)
    :returns:   True if before is newer than seconds else False
    :rtype: bool
    """
    return after - utcnow() > datetime.timedelta(seconds=seconds)


def delta_seconds(before, after):
    """Return the difference between two timing objects.

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
    """Return the total seconds of datetime.timedelta object.

    :param timedelta delta: a delta to convert
    :returns:   seconds
    :rtype:     int
    """
    return delta.total_seconds()


# Defined here such that total_seconds is properly defined prior to usage
ONE_WEEK = total_seconds(datetime.timedelta(weeks=1))
