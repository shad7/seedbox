"""
Provides the ability to perform maintenance on a database.
"""
import logging
import os
import shutil

import six.moves.urllib.parse as urlparse

LOG = logging.getLogger(__name__)
# total of 8 weeks/2 months of backups
MAX_BACKUP_COUNT = 8


def backup(conf):
    """
    create a backup copy of the database file.

    :param oslo.config.cfg.ConfigOpts conf: an instance of configuration
    """

    LOG.debug('starting database backup process')
    default_db_name = urlparse.urlparse(
        conf.database.connection).path.replace('//', '/')
    LOG.debug('location of database: [%s]', default_db_name)
    if os.path.exists(default_db_name):
        for i in range(MAX_BACKUP_COUNT - 1, 0, -1):
            sfn = '%s.%d' % (default_db_name, i)
            dfn = '%s.%d' % (default_db_name, i + 1)
            if os.path.exists(sfn):
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(sfn, dfn)
        dfn = default_db_name + '.1'
        LOG.info('backing up db [%s] to [%s]', default_db_name, dfn)
        shutil.copy2(default_db_name, dfn)
        LOG.info('backup complete')
    else:
        LOG.warning('Database [%s] does not exist, no backup taken.',
                    default_db_name)
