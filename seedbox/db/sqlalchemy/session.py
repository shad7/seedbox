"""
Manages connection to the database via sqlalchemy
"""
import logging

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy import orm
from sqlalchemy import pool

LOG = logging.getLogger(__name__)


def receive_connect(dbapi_con, con_record):
    """
    Ensures that the foreign key constraints are enforced in SQLite.

    The foreign key constraints are disabled by default in SQLite,
    so the foreign key constraints will be enabled here for every
    database connection

    :param dbapi_con: database connection
    :param con_record: connection record
    """
    dbapi_con.execute('pragma foreign_keys=ON')


def create_engine(sql_connection, idle_timeout=3600, connection_debug=0):
    """Return a new SQLAlchemy engine.

    :param sql_connection: sql connection string
    :param idle_timeout: timeout period the connection can be idle
    :param connection_debug: enable debugging for the connection
    """

    logger = logging.getLogger('sqlalchemy.engine')

    # Map SQL debug level to Python log level
    if connection_debug >= 100:
        logger.setLevel(logging.DEBUG)
    elif connection_debug >= 50:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    engine_args = {
        'pool_recycle': idle_timeout,
        'convert_unicode': True,
        'poolclass': pool.NullPool,
        'connect_args': {'check_same_thread': False},
    }

    engine = sa.create_engine(sql_connection, **engine_args)
    # will associate with engine.pool
    event.listen(engine, 'connect', receive_connect)
    engine.connect()
    return engine


def get_maker(engine):
    """Return a SQLAlchemy sessionmaker using the given engine.

    :param engine: a database connection engine
    """
    return orm.sessionmaker(bind=engine, autocommit=True)


class EngineFacade(object):
    """
    A helper class that creates engine and sessionmaker
    on its instantiation and provides get_engine()/get_session() methods.

    engine/sessionmaker instances will be global.

    Note: Two important things to remember:

    1. An Engine instance is effectively a pool of DB connections, so it's
       meant to be shared (and it's thread-safe).
    2. A Session instance is not meant to be shared and represents a DB
       transactional context (i.e. it's not thread-safe). sessionmaker is
       a factory of sessions.

    """

    def __init__(self, sql_connection, **kwargs):
        """Initialize engine and sessionmaker instances.

        Keyword arguments:

        :keyword idle_timeout: timeout before idle sql connections are reaped
                               (defaults to 3600)
        :keyword connection_debug: verbosity of SQL debugging information.
                                   0=None, 100=Everything (defaults to 0)
        """
        self._engine = create_engine(
            sql_connection=sql_connection,
            idle_timeout=kwargs.get('idle_timeout', 3600),
            connection_debug=kwargs.get('connection_debug', 0))
        self._session_maker = get_maker(engine=self._engine)

    @property
    def engine(self):
        """Get the engine instance (note, that it's shared)."""
        return self._engine

    @property
    def session_maker(self):
        """Get the session maker instance"""
        return self._session_maker

    @property
    def session(self):
        """Get a Session instance."""
        return self._session_maker()

    @classmethod
    def from_config(cls, connection_string, conf):
        """Initialize EngineFacade using oslo.config config instance options.

        :param connection_string: SQLAlchemy connection string
        :type connection_string: string

        :param conf: oslo.config config instance
        :type conf: oslo.config.cfg.ConfigOpts

        """
        LOG.debug('making connection using connect string: %s',
                  connection_string)
        return cls(sql_connection=connection_string,
                   **dict(conf.database.items()))
