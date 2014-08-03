from datetime import datetime
import sqlalchemy as sa
import testtools

from seedbox.db.sqlalchemy import models
from seedbox.db.sqlalchemy import session
from seedbox.tests import test


class FakeTable(models.Base, models.HasId, models.HasTimestamp):

    __table_args__ = {
        'sqlite_autoincrement':  True,
    }

    name = sa.Column(sa.String(255))
    val = sa.Column(sa.String(255))


class SAModelsTestCase(test.BaseTestCase):

    def setUp(self):
        super(SAModelsTestCase, self).setUp()

        self.facade = session.EngineFacade('sqlite:///:memory:')
        models.verify_tables(self.facade.engine)

    def tearDown(self):
        models.purge_all_tables(self.facade.engine)
        super(SAModelsTestCase, self).tearDown()

    def test_base(self):

        self.assertEqual(FakeTable.__tablename__, 'fake_tables')

        _row = FakeTable()
        _row['name'] = 'sample'
        _row['val'] = 'a1234'
        self.assertIsNotNone(_row)
        self.assertIsNotNone(repr(_row))

        self.assertEqual(_row['name'], 'sample')

        for i in _row:
            self.assertIn(i[0],
                          ['id', 'name', 'val', 'created_at', 'updated_at'])

        for k, v in _row.iteritems():
            self.assertIn(k,
                          ['id', 'name', 'val', 'created_at', 'updated_at'])

        values = dict(name='sample1', val='b56789')
        _row.update(values)
        self.assertEqual(_row['name'], 'sample1')

    def test_torrent(self):
        self.assertEqual(models.Torrent.__tablename__, 'torrents')

    def test_mediafile(self):
        self.assertEqual(models.MediaFile.__tablename__, 'media_files')

    def test_appstate(self):
        self.assertEqual(models.AppState.__tablename__, 'app_states')

        str_state = models.AppState('str_state', 'astring')
        self.assertIsNotNone(repr(str_state))
        self.assertEqual(str_state.get_value(), 'astring')

        str_state['id'] = 'str_state1'
        self.assertEqual(str_state.get_value(), 'astring')
        str_state['value'] = 'bstring'
        self.assertEqual(str_state.get_value(), 'bstring')

        self.assertEqual(str_state['id'], 'str_state1')
        self.assertEqual(str_state['value'], 'bstring')
        self.assertEqual(str_state['t_string'], 'bstring')

        altstr1_state = models.AppState('str_state', None)
        self.assertEqual(altstr1_state.get_value(), None)

        models.AppState('str_state', u'ustring')

        int_state = models.AppState('int_state', 7)
        self.assertEqual(int_state.get_value(), 7)

        bool_state = models.AppState('bool_state', True)
        self.assertEqual(bool_state.get_value(), True)

        values = {'value': False}
        bool_state.update(values)
        self.assertEqual(bool_state.get_value(), False)

        _date = datetime.utcnow()
        date_state = models.AppState('date_state', _date)
        self.assertEqual(date_state.get_value(), _date)

        models.AppState('date_state', datetime.utcnow().date())

        with testtools.ExpectedException(TypeError):
            str_state.set_value(object())

        with testtools.ExpectedException(TypeError):
            models.AppState('str_state', object())

    def test_query_transform(self):

        transformer = models.QueryTransformer(
            models.Torrent, self.facade.session.query(models.Torrent))

        qfilter = {'=': {'name': 'test'}}
        _query = transformer.apply_filter(qfilter)
        self.assertIsNotNone(_query.statement)

        qfilter = {'and': [{'=': {'invalid': False}},
                           {'=': {'purged': False}},
                           {'=': {'failed': False}},
                           {'in': {'state': ['init', 'ready', 'active']}}
                           ]}
        _query = transformer.apply_filter(qfilter)
        self.assertIsNotNone(_query.statement)

        qfilter = {'not': {'=': {'name': 'test'}}}
        _query = transformer.apply_filter(qfilter)
        self.assertIsNotNone(_query.statement)
