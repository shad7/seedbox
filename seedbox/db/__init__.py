import copy
import logging

from oslo.config import cfg
import six.moves.urllib.parse as urlparse
from stevedore import driver

from seedbox.db import api

LOG = logging.getLogger(__name__)
DB_ENGINE_NAMESPACE = 'seedbox.db'

database_opts = [
    cfg.StrOpt('connection',
               default='sqlite:///$config_dir/torrent.db',
               secret=True,
               help='The connection string used to connect to the database'),
    cfg.IntOpt('idle_timeout',
               default=3600,
               help='Timeout before idle sql connections are reaped'),
    cfg.IntOpt('connection_debug',
               default=0,
               help='Verbosity of SQL debugging information. 0=None, 100=All'),
]

cfg.CONF.register_opts(database_opts, 'database')

_DBAPI = None


def _get_connection(conf):
    """Load the configured engine and return an instance."""
    engine_name = urlparse.urlparse(conf.database.connection).scheme
    LOG.debug('looking for %s driver in %s', engine_name, DB_ENGINE_NAMESPACE)
    mgr = driver.DriverManager(DB_ENGINE_NAMESPACE, engine_name)
    return mgr.driver(conf)


def dbapi(conf=cfg.CONF):
    global _DBAPI

    if _DBAPI is None:
        _DBAPI = api.DBApi(_get_connection(conf))
        _DBAPI.shrink_db()
    return _DBAPI


def list_opts():
    """
    Returns a list of oslo.config options available in the library.

    The returned list includes all oslo.config options which may be registered
    at runtime by the library.

    Each element of the list is a tuple. The first element is the name of the
    group under which the list of elements in the second element will be
    registered. A group name of None corresponds to the [DEFAULT] group in
    config files.

    The purpose of this is to allow tools like the Oslo sample config file
    generator to discover the options exposed to users by this library.

    :returns: a list of (group_name, opts) tuples
    """
    return [('database', copy.deepcopy(database_opts))]
