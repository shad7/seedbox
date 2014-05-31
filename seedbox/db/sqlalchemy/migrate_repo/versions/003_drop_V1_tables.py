import sqlalchemy as sa


def upgrade(migrate_engine):
    meta = sa.MetaData(bind=migrate_engine)

    appstates = sa.Table('app_state', meta)
    appstates.drop(checkfirst=True)

    torrents = sa.Table('torrent', meta)
    torrents.drop(checkfirst=True)

    medias = sa.Table('media_file', meta)
    medias.drop(checkfirst=True)


def downgrade(migrate_engine):
    pass
