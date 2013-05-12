"""
A class that defines a torrent file and the associated state. Also defined is a class
that defines the contents of a torrent file, ie some media files typically.
"""
from __future__ import absolute_import
from sqlobject import *
import logging
import os, sys
import shutil

log = logging.getLogger(__name__)
DB_NAME = 'torrent.db'
MAX_BACKUP_COUNT = 12

class Torrent(SQLObject):
    """
    A class that defines a torrent and associated database table using
    SQLObjects to handle persistence.
    """
    name = StringCol(unique=True)
    create_date = DateCol(default=DateTimeCol.now)
    state = EnumCol(enumValues=['init', 'ready', 'active', 'done', 'cancelled'], default='init')
    retry_count = IntCol(default=0)
    failed = BoolCol(default=False)
    error_msg = StringCol(default=None)
    invalid = BoolCol(default=False)
    purged = BoolCol(default=False)
    media_files = SQLMultipleJoin('MediaFile')

class MediaFile(SQLObject):
    """
    A class that defines a media file contained within a torrent file
    and associatd database table using SQLObjects to handle persistence.
    """

    filename = StringCol()
    file_ext = StringCol()
    file_path = StringCol(default=None)
    size = IntCol(default=0)
    compressed = BoolCol(default=False)
    synced = BoolCol(default=False)
    missing = BoolCol(default=False)
    skipped = BoolCol(default=False)
    torrent = ForeignKey('Torrent', cascade=True)

class AppState(SQLObject):
    """
    A class that defines maintains information about the state of the application
    and internal processing. Effectively it is just a key-value pair except we
    store the values by type.
    """

    name = StringCol(unique=True)
    val_str = StringCol(default=None)
    val_int = IntCol(default=-99999)
    val_list = StringCol(default=None)
    val_flag = BoolCol(default=False)
    val_date = DateTimeCol(default=DateTimeCol.now)


def init(resource_path, reset=False):
    """
    Establish a connection and make sure all structures are in place
    """

    dbloc = os.path.join(resource_path, DB_NAME)
    log.trace('location of database will be: [%s]', dbloc)
    db_exists = False
    if os.path.exists(dbloc):
        db_exists = True
        log.info('loading database [%s]', dbloc)
    else:
        log.info('database does not exist; creating database....[%s]', dbloc)

    connect_str = '{0}{1}{2}'.format('sqlite:', dbloc, '?driver=sqlite3')
    log.trace('establishing connection to database: [%s]', connect_str)
    # create connection to the database
    sqlhub.processConnection = connectionForURI(connect_str)

    # if the database already existed and a reset was requested then
    # we drop all the tables
    if db_exists and reset:
        log.info('reset requested; deleting database cache.')
        Torrent.dropTable(ifExists=True)
        MediaFile.dropTable(ifExists=True)
        AppState.dropTable(ifExists=True)
        log.info('recreating database cache....')

    # we have defined the class, so create the table if it doesn't exist
    Torrent.createTable(ifNotExists=True)

    # we have defined the class, so create the table if it doesn't exist
    MediaFile.createTable(ifNotExists=True)

    # we have defined the class, so create the table if it doesn't exist
    AppState.createTable(ifNotExists=True)

    if log.isEnabledFor(logging.DEBUG):
        log.trace('Torrent table: [%s]', Torrent.sqlmeta.table)
        log.trace('Torrent Columns: [%s]', Torrent.sqlmeta.columns.keys())
    
        log.trace('MediaFile table: [%s]', MediaFile.sqlmeta.table)
        log.trace('MediaFile Columns: [%s]', MediaFile.sqlmeta.columns.keys())

        log.trace('AppState table: [%s]', AppState.sqlmeta.table)
        log.trace('AppState Columns: [%s]', AppState.sqlmeta.columns.keys())


def backup(resource_path):
    """
    create a copy of myself
    """
    log.trace('starting database backup process')
    default_db_name = os.path.abspath(os.path.join(resource_path, DB_NAME))
    log.trace('location of database: [%s]', default_db_name)
    if os.path.exists(default_db_name):
        for i in range(MAX_BACKUP_COUNT - 1, 0, -1):
            sfn = '%s.%d' % (default_db_name, i)
            dfn = '%s.%d' % (default_db_name, i + 1)
            if os.path.exists(sfn):
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(sfn, dfn)
        dfn = default_db_name + '.1'
        if os.path.exists(dfn):
            os.remove(dfn)
        log.info('backing up db [%s] to [%s]', default_db_name, dfn)
        shutil.copy2(default_db_name, dfn)
        if os.path.exists(dfn):
            log.info('backup complete')
        else:
            log.error('no exceptions raised, but backup file does not exist!')
    else:
        log.warn('Database [%s] does not exist, no backup taken.', default_db_name)

