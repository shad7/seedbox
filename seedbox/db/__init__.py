"""Provides access to database API for interacting with the torrent data."""
import logging

from oslo_config import cfg
import six.moves.urllib.parse as urlparse
from stevedore import driver

from seedbox.db import api

LOG = logging.getLogger(__name__)
DB_ENGINE_NAMESPACE = 'seedbox.db'

cfg.CONF.import_group('database', 'seedbox.options')

_DBAPI = {}


def _get_connection(conf):
    """Load the configured engine and return an instance."""
    engine_name = urlparse.urlparse(conf.database.connection).scheme
    LOG.debug('looking for %s driver in %s', engine_name, DB_ENGINE_NAMESPACE)
    mgr = driver.DriverManager(DB_ENGINE_NAMESPACE, engine_name)
    return mgr.driver(conf)


def dbapi(conf=cfg.CONF):
    """Retrieves an instance of the configured database API.

    :param oslo_config.cfg.ConfigOpts conf: an instance of the configuration
                                            file
    :return: database API instance
    :rtype: :class:`~seedbox.db.api.DBApi`
    """
    if not _DBAPI:
        _DBAPI[DB_ENGINE_NAMESPACE] = api.DBApi(_get_connection(conf))
        _DBAPI[DB_ENGINE_NAMESPACE].shrink_db()
    return _DBAPI[DB_ENGINE_NAMESPACE]
