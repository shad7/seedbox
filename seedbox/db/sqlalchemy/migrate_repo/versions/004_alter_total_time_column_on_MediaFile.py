"""Handles converting MediaFile.total_time from Integer to Float"""
import sqlalchemy as sa


def upgrade(migrate_engine):
    meta = sa.MetaData(bind=migrate_engine)
    table = sa.Table('media_files', meta, autoload=True)
    col_resource = getattr(table.c, 'total_time')
    # converts Integer to Float
    col_resource.alter(type=sa.Float)


def downgrade(migrate_engine):
    meta = sa.MetaData(bind=migrate_engine)
    table = sa.Table('media_files', meta, autoload=True)
    col_resource = getattr(table.c, 'total_time')
    # converts Float to Integer
    col_resource.alter(type=sa.Integer)
