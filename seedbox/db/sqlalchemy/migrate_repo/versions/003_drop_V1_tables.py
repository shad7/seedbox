"""
Provides removing the initial version of the database tables for clean up
purposes.
"""
import sqlalchemy as sa


def upgrade(migrate_engine):
    """
    Drops the initial version of the tables.

    :param migrate_engine: an instance of database connection engine
    """
    meta = sa.MetaData(bind=migrate_engine)

    appstates = sa.Table('app_state', meta)
    appstates.drop(checkfirst=True)

    torrents = sa.Table('torrent', meta)
    torrents.drop(checkfirst=True)

    medias = sa.Table('media_file', meta)
    medias.drop(checkfirst=True)


def downgrade(migrate_engine):
    """
    Does nothing since the ability to go version 1 from 3 is not supported
    directly.

    :param migrate_engine: an instance of database connection engine
    """
    pass
