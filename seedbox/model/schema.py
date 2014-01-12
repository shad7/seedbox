"""
A class that defines a torrent file and the associated state. Also defined
is a class that defines the contents of a torrent file, ie some media
files typically.
"""
from __future__ import absolute_import
import sqlobject
import logging
import os
import shutil
from oslo.config import cfg

log = logging.getLogger(__name__)
DB_NAME = 'torrent.db'
MAX_BACKUP_COUNT = 12


class Torrent(sqlobject.SQLObject):
    """
    A class that defines a torrent and associated database table using
    SQLObjects to handle persistence.

    .. py:attribute:: name
        the name of torrent file (required; primary key)
    .. py:attribute:: create_date
        the datetime timestamp of when record was created in db
    .. py:attribute:: state
        state/phase associated with Torrent
        ['init', 'ready', 'active', 'done', 'cancelled']
        default='init'
    .. py:attribute:: retry_count
        a counter for the number of retry attempts
    .. py:attribute:: failed
        flag to indicate if the Torrent failed during processing
    .. py:attribute:: error_msg
        and exception message capture when a failure happened
    .. py:attribute:: invalid
        flag to indicate if the Torrent is invalid (parsing failed)
    .. py:attribute:: purged
        flag to indicate if the Torrent was purged
    .. py:attribute:: media_files
        reference to a collection of MediaFile records
    """
    name = sqlobject.StringCol(unique=True)
    create_date = sqlobject.DateCol(default=sqlobject.DateTimeCol.now)
    state = sqlobject.EnumCol(enumValues=['init',
                                          'ready',
                                          'active',
                                          'done',
                                          'cancelled'],
                              default='init')
    retry_count = sqlobject.IntCol(default=0)
    failed = sqlobject.BoolCol(default=False)
    error_msg = sqlobject.StringCol(default=None)
    invalid = sqlobject.BoolCol(default=False)
    purged = sqlobject.BoolCol(default=False)
    media_files = sqlobject.SQLMultipleJoin('MediaFile')


class MediaFile(sqlobject.SQLObject):
    """
    A class that defines a media file contained within a torrent file
    and associatd database table using SQLObjects to handle persistence.

    .. py:attribute:: filename
        the name of the file associated with media
    .. py:attribute:: file_ext
        the file type extension associated with media
    .. py:attribute:: file_path
        the location where the media file is stored
    .. py:attribute:: size
        the size in bytes of the media file
    .. py:attribute:: compressed
        flag indicating if the media file is compressed
    .. py:attribute:: synced
        flag indicating if the media file is synced back to home
        library from seedbox
    .. py:attribute:: missing
        flag indicating if the media file was missing from folder
    .. py:attribute:: skipped
        flag indicating if the media file was skipped for processing
    .. py:attribute:: torrent
        foreign key reference to the associated Torrent
    """

    filename = sqlobject.StringCol()
    """the name of the file associated with media"""
    file_ext = sqlobject.StringCol()
    file_path = sqlobject.StringCol(default=None)
    size = sqlobject.IntCol(default=0)
    compressed = sqlobject.BoolCol(default=False)
    synced = sqlobject.BoolCol(default=False)
    missing = sqlobject.BoolCol(default=False)
    skipped = sqlobject.BoolCol(default=False)
    torrent = sqlobject.ForeignKey('Torrent', cascade=True)


class AppState(sqlobject.SQLObject):
    """
    A class that defines maintains information about the state of the
    application and internal processing. Effectively it is just a
    key-value pair except we store the values by type.

    .. py:attribute:: name
        an identifer for the state
    .. py:attribute:: val_str
        a value of type string
    .. py:attribute:: val_int
        a value of type int
    .. py:attribute:: val_list
        a value of type list
    .. py:attribute:: val_flag
        a value of type boolean
    .. py:attribute:: val_date
        a value of type date
    """

    name = sqlobject.StringCol(unique=True)
    val_str = sqlobject.StringCol(default=None)
    val_int = sqlobject.IntCol(default=-99999)
    val_list = sqlobject.StringCol(default=None)
    val_flag = sqlobject.BoolCol(default=False)
    val_date = sqlobject.DateTimeCol(default=sqlobject.DateTimeCol.now)


def init():
    """
    Establish a connection and make sure all structures are in place
    """

    dbloc = os.path.join(cfg.CONF.config_dir, DB_NAME)
    log.trace('location of database will be: [%s]', dbloc)
    db_exists = False
    if os.path.exists(dbloc):
        db_exists = True
        log.debug('loading database [%s]', dbloc)
    else:
        log.info('database does not exist; creating database....[%s]', dbloc)

    connect_str = '{0}{1}{2}'.format('sqlite:', dbloc, '?driver=sqlite3')
    log.trace('establishing connection to database: [%s]', connect_str)
    # create connection to the database
    sqlobject.sqlhub.processConnection = sqlobject.connectionForURI(
        connect_str)

    # if the database already existed and a purge was requested then
    # we drop all the tables
    if db_exists and cfg.CONF.purge:
        log.info('purge requested; deleting database cache.')
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


def backup():
    """
    create a backup copy of the database file.
    """
    log.trace('starting database backup process')
    default_db_name = os.path.abspath(os.path.join(cfg.CONF.config_dir,
                                                   DB_NAME))
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
        log.info('backing up db [%s] to [%s]', default_db_name, dfn)
        shutil.copy2(default_db_name, dfn)
        log.info('backup complete')
    else:
        log.warn('Database [%s] does not exist, no backup taken.',
                 default_db_name)
