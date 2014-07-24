"""
Migrates to version 2 of the database tables and supports downgrading to
previous version.
"""
from datetime import datetime

import sqlalchemy as sa

STATES = ['init', 'ready', 'active', 'done', 'cancelled']
VAL_TYPES = ['none', 'bool', 'datetime', 'int', 'str']


def upgrade(migrate_engine):
    """
    Updates table model to new version and moves existing data from old
    structures to the new structure.

    :param migrate_engine: an instance of database connection engine
    """
    meta = sa.MetaData(bind=migrate_engine)

    appstates = sa.Table(
        'app_states', meta,
        sa.Column('name', sa.String(255), primary_key=True),
        sa.Column('dtype', sa.Enum(*VAL_TYPES), default='none'),
        sa.Column('t_string', sa.String(255), nullable=True, default=None),
        sa.Column('t_int', sa.Integer, nullable=True, default=None),
        sa.Column('t_bool', sa.Boolean, nullable=True, default=None),
        sa.Column('t_datetime', sa.DateTime, nullable=True, default=None))
    appstates.create(checkfirst=True)

    v1_appstate = sa.Table('app_state', meta, autoload=True)
    for row in v1_appstate.select().execute().fetchall():
        # currently there will only be one at this time in the
        # lifecycle of the application.
        data = {
            'name': row.name,
            'dtype': 'datetime',
            't_datetime': row.val_date
        }
        appstates.insert().values(**data).execute()

    torrents = sa.Table(
        'torrents', meta,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=datetime.utcnow),
        sa.Column('name', sa.String(255), unique=True),
        sa.Column('state', sa.Enum(*STATES), default='init'),
        sa.Column('retry_count', sa.Integer, default=0),
        sa.Column('failed', sa.Boolean, default=False),
        sa.Column('error_msg', sa.String(5000), default=None),
        sa.Column('invalid', sa.Boolean, default=False),
        sa.Column('purged', sa.Boolean, default=False))
    torrents.create(checkfirst=True)

    v1_torrent = sa.Table('torrent', meta, autoload=True)
    for row in v1_torrent.select().execute().fetchall():
        data = dict(row)
        data['created_at'] = data.pop('create_date')
        torrents.insert().values(**data).execute()

    medias = sa.Table(
        'media_files', meta,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('filename', sa.String(255)),
        sa.Column('file_ext', sa.String(30)),
        sa.Column('file_path', sa.String(1000), default=None),
        sa.Column('size', sa.Integer, default=0),
        sa.Column('compressed', sa.Boolean, default=False),
        sa.Column('synced', sa.Boolean, default=False),
        sa.Column('missing', sa.Boolean, default=False),
        sa.Column('skipped', sa.Boolean, default=False),
        sa.Column('error_msg', sa.String(500), default=None),
        sa.Column('total_time', sa.Integer, default=0),
        sa.Column('torrent_id', sa.Integer, sa.ForeignKey('torrents.id')))
    medias.create(checkfirst=True)

    v1_media = sa.Table('media_file', meta, autoload=True)
    for row in v1_media.select().execute().fetchall():
        medias.insert().values(**dict(row)).execute()


def downgrade(migrate_engine):
    """
    Converts back to previous version and removes the newly created tables.

    :param migrate_engine: an instance of database connection engine
    """
    meta = sa.MetaData(bind=migrate_engine)

    appstates = sa.Table('app_states', meta)
    appstates.drop(checkfirst=True)

    torrents = sa.Table('torrents', meta)
    torrents.drop(checkfirst=True)

    medias = sa.Table('media_files', meta)
    medias.drop(checkfirst=True)
