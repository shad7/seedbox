"""
Private database API implemented for sqlalchemy for database operations.
"""
import logging

from seedbox.db import base
from seedbox.db import maintenance
from seedbox.db.sqlalchemy import migration
from seedbox.db.sqlalchemy import model_util
from seedbox.db.sqlalchemy import models as db_model
from seedbox.db.sqlalchemy import session as db_session

LOG = logging.getLogger(__name__)


class Connection(base.Connection):
    """SQLAlchemy connection."""

    def __init__(self, conf):
        """
        :param conf: an instance of configuration file
        :type conf: oslo.config.cfg.ConfigOpts
        """
        super(Connection, self).__init__(conf)
        self._engine_facade = db_session.EngineFacade.from_config(
            conf.database.connection, conf)
        self.upgrade()

    def upgrade(self):
        """Migrate the database to `version` or most recent version."""
        engine = self._engine_facade.engine
        migration.db_sync(engine)
        engine.dispose()

    def clear(self):
        """Clear database."""
        engine = self._engine_facade.engine
        db_model.purge_all_tables(engine)
        self._engine_facade.session_maker.close_all()
        engine.dispose()

    def backup(self):
        """Backup database."""
        maintenance.backup(self.conf)

    def shrink_db(self):
        """Shrink database."""
        engine = self._engine_facade.engine
        with engine.begin() as conn:
            conn.execute('VACUUM')
            LOG.debug('db space reclaimed')

    def save(self, instance):
        """Save the instance to the database

        :param instance: an instance of modeled data object
        """
        _model = getattr(db_model, instance.__class__.__name__)
        session = self._engine_facade.session
        with session.begin():
            _pk = getattr(instance, instance.PK_NAME)
            if _pk is not None:
                _row = session.query(_model).get(_pk)
                _row = model_util.to_db(instance, _row)
            else:
                _row = model_util.to_db(instance)
                session.add(_row)
            _row.save(session)
        return model_util.from_db(_row)

    def bulk_create(self, instances):
        """Save the instances in bulk to the database.

        :param list instances: a list of instance of modeled data object
        """
        if not instances:
            return
        _instances = [model_util.to_db(item) for item in instances]

        session = self._engine_facade.session
        with session.begin():
            session.add_all(_instances)
        for _row in _instances:
            yield model_util.from_db(_row)

    def bulk_update(self, value_map, entity_type, qfilter):
        """
        Perform bulk save based on filter criteria with values
        from value map to the database.

        :param dict value_map: a dict of key-value pairs representing the
                               data of an instance.
        :param class entity_type: the model type
        :param dict qfilter: query filter to determine which rows to update
        """
        _model = getattr(db_model, entity_type.__name__)
        session = self._engine_facade.session
        with session.begin():
            transformer = db_model.QueryTransformer(_model,
                                                    session.query(_model))
            _query = transformer.apply_filter(qfilter)
            total = _query.update(value_map, synchronize_session=False)
            LOG.debug('total rows updated: %d', total)

    def delete_by(self, entity_type, qfilter):
        """Delete instances of a specific type based on filter criteria

        :param entity_type: the model type
        :param qfilter: query filter to determine which rows to update
        """
        _model = getattr(db_model, entity_type.__name__)
        session = self._engine_facade.session
        with session.begin():
            transformer = db_model.QueryTransformer(_model,
                                                    session.query(_model))
            _query = transformer.apply_filter(qfilter)
            total = _query.delete(synchronize_session=False)
            LOG.debug('total rows deleted: %d', total)

    def delete(self, instance):
        """Delete the instance(s) based on filter from the database.

        :param instance: an instance of modeled data object
        """
        _model = getattr(db_model, instance.__class__.__name__)
        session = self._engine_facade.session
        with session.begin():
            _row = session.query(_model).get(getattr(instance,
                                                     instance.PK_NAME))
            if _row:
                session.delete(_row)
                LOG.debug('total rows deleted: 1')
            else:
                LOG.debug('no rows deleted')

    def fetch_by(self, entity_type, qfilter):
        """Fetch the instance(s) based on filter from the database.

        :param entity_type: the model type
        :param qfilter: query filter to determine which rows to update
        """
        _model = getattr(db_model, entity_type.__name__)
        session = self._engine_facade.session
        with session.begin():
            transformer = db_model.QueryTransformer(_model,
                                                    session.query(_model))
            _query = transformer.apply_filter(qfilter)
            for _row in _query.all():
                yield model_util.from_db(_row)

    def fetch(self, entity_type, pk):
        """Fetch the instance using primary key from the database.

        :param entity_type: the model type
        :param pk: primary key value
        """
        _model = getattr(db_model, entity_type.__name__)
        session = self._engine_facade.session
        with session.begin():
            _row = session.query(_model).get(pk)
        return model_util.from_db(_row)
