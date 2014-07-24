# Copyright (c) 2013 OpenStack Foundation
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Base on code in migrate/changeset/databases/sqlite.py which is under
# the following license:
#
# The MIT License
#
# Copyright (c) 2009 Evan Rosson, Jan Dittberner, Domen Kozar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Provides ability to manage versions of database models
"""
import os

from migrate import exceptions as versioning_exceptions
from migrate.versioning import api as versioning_api
from migrate.versioning.repository import Repository

from seedbox.db import exception

INIT_VERSION = 0
_REPO = None


def db_sync(engine, version=None, init_version=INIT_VERSION):
    """
    Upgrade or downgrade a database.

    Function runs the upgrade() or downgrade() functions in change scripts.

    :param engine:       SQLAlchemy engine instance for a given database
    :param version:      Database will upgrade/downgrade until this version.
                         If None - database will update to the latest
                         available version.
    :param init_version: Initial database version
    """

    if version is not None:
        try:
            version = int(version)
        except ValueError:
            raise exception.DbMigrationError(
                message='version should be an integer')

    current_version = db_version(engine, init_version)
    repository = _find_migrate_repo()
    if version is None or version > current_version:
        return versioning_api.upgrade(engine, repository, version)
    else:
        return versioning_api.downgrade(engine, repository, version)


def db_version(engine, init_version=INIT_VERSION):
    """
    Show the current version of the repository.

    :param engine:  SQLAlchemy engine instance for a given database
    :param init_version:  Initial database version
    """
    repository = _find_migrate_repo()
    try:
        return versioning_api.db_version(engine, repository)
    except versioning_exceptions.DatabaseNotControlledError:
        db_version_control(engine, init_version)
        return versioning_api.db_version(engine, repository)


def db_version_control(engine, version=None):
    """
    Mark a database as under this repository's version control.

    Once a database is under version control, schema changes should
    only be done via change scripts in this repository.

    :param engine:  SQLAlchemy engine instance for a given database
    :param version:  Initial database version
    """
    versioning_api.version_control(engine, _find_migrate_repo(), version)


def _find_migrate_repo():
    """
    Get the project's change script repository
    """
    global _REPO

    if _REPO is None:
        abspath = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'migrate_repo')
        _REPO = Repository(abspath)
    return _REPO
