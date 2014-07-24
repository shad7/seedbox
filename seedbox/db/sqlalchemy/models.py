"""
Provides database model compliant with sqlalchemy.
"""
import datetime
import operator
import re

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext import declarative

from seedbox import constants

NONE_TYPE = 'none'
BOOL_TYPE = 'bool'
DATE_TYPE = 'datetime'
INT_TYPE = 'int'
STR_TYPE = 'str'
VAL_TYPES = [NONE_TYPE, BOOL_TYPE, DATE_TYPE, INT_TYPE, STR_TYPE]


def to_table_name(klass_name):
    """
    Convention is to take camel-case class name and rewrite it to an
    underscore form, e.g. 'ClassName' to 'class_name'

    :param klass_name: name of class
    :return: properly formatted table name
    :rtype: string
    """
    return re.sub('[A-Z]+',
                  lambda i: '_' + i.group(0).lower(),
                  klass_name).lstrip('_') + 's'


@declarative.as_declarative()
class Base(six.Iterator):
    """
    Represents a Base class mapped to table in the database.
    """

    @declarative.declared_attr
    def __tablename__(cls):
        return to_table_name(cls.__name__)

    def save(self, session):
        """Save this object.
        :param session: a database connection session
        """
        with session.begin(subtransactions=True):
            session.add(self)
            session.flush()

    def __repr__(self):
        """sqlalchemy based automatic __repr__ method."""
        items = ['%s=%r' % (col.name, getattr(self, col.name))
                 for col in self.__table__.columns]
        return '<%s.%s[object at %x] {%s}>' % (self.__class__.__module__,
                                               self.__class__.__name__,
                                               id(self), ', '.join(items))

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        """
        Retrieve value for an attribute in the table.

        :param key: name of field/attribute
        :param default: default value if not found
        :return: attribute value :rtype: varied
        """
        return getattr(self, key, default)

    def __iter__(self):
        self._i = iter(list(dict(orm.object_mapper(self).columns).keys()))
        return self

    def __next__(self):
        n = six.advance_iterator(self._i)
        return n, getattr(self, n)

    def next(self):
        """
        Using an iterator to get next attribute value from generator

        :return: attribute, attribute value
        :rtype: tuple
        """
        return self.__next__()

    def update(self, values):
        """Make the model object behave like a dict.

        :param values: key-value pairs of attributes and values
        """
        for k, v in six.iteritems(values):
            setattr(self, k, v)

    def iteritems(self):
        """
        an iterator over dictionary items

        :return: dictionary items
        :rtype: iterator
        """
        local = dict(self)
        joined = dict([(k, v) for k, v in six.iteritems(self.__dict__)
                      if not k[0] == '_'])
        local.update(joined)
        return six.iteritems(local)


class HasId(object):
    """
    Table mixin providing a class/table id attribute
    """
    id = sa.Column(sa.Integer, primary_key=True)


class HasTimestamp(object):
    """
    Table mixin providing a class/table date attributes
    """
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, onupdate=datetime.datetime.utcnow)


class Torrent(Base, HasId, HasTimestamp):
    """
    Class representing a torrent in the database
    """

    __table_args__ = {
        'sqlite_autoincrement':  True,
    }

    name = sa.Column(sa.String(255), unique=True)
    state = sa.Column(sa.Enum(*constants.STATES), default=constants.INIT)
    retry_count = sa.Column(sa.Integer, default=0)
    failed = sa.Column(sa.Boolean, default=False)
    error_msg = sa.Column(sa.String(5000), default=None)
    invalid = sa.Column(sa.Boolean, default=False)
    purged = sa.Column(sa.Boolean, default=False)
    media_files = orm.relationship('MediaFile', backref='torrents',
                                   cascade='all, delete-orphan')


class MediaFile(Base, HasId):
    """
    Class representing a media file in the database
    """

    __table_args__ = {
        'sqlite_autoincrement':  True,
    }

    filename = sa.Column(sa.String(255))
    file_ext = sa.Column(sa.String(30))
    file_path = sa.Column(sa.String(1000), default=None)
    size = sa.Column(sa.Integer, default=0)
    compressed = sa.Column(sa.Boolean, default=False)
    synced = sa.Column(sa.Boolean, default=False)
    missing = sa.Column(sa.Boolean, default=False)
    skipped = sa.Column(sa.Boolean, default=False)
    error_msg = sa.Column(sa.String(500), default=None)
    total_time = sa.Column(sa.Integer, default=0)
    torrent_id = sa.Column(sa.Integer, sa.ForeignKey('torrents.id'))


class AppState(Base):

    """
    Class representing an app state in the database

    :param id: primary key of app state (alias for name)
    :type id: string
    :param value: value of the app state
    :type value: string, int, bool, or datetime
    """
    name = sa.Column(sa.String(255), primary_key=True)
    dtype = sa.Column(sa.Enum(*VAL_TYPES), default=NONE_TYPE)
    t_string = sa.Column(sa.String(255), nullable=True, default=None)
    t_int = sa.Column(sa.Integer, nullable=True, default=None)
    t_bool = sa.Column(sa.Boolean, nullable=True, default=None)
    t_datetime = sa.Column(sa.DateTime, nullable=True, default=None)

    def __init__(self, id, value=None):
        self.name = id
        self.set_value(value)

    def __setitem__(self, key, value):
        if key in ['id', 'name']:
            self.name = value
        if key == 'value':
            self.set_value(value)

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, default=None):
        """
        Overrides base class get method to handle primary key of app state

        :param key: id/name of app state
        :param default: default value if not found
        :return: an appstate value attribute
        :rtype: varies
        """
        if key in ['id', 'name']:
            return self.name
        if key == 'value':
            return self.get_value()
        return getattr(self, key, default)

    def update(self, values):
        """Make the model object behave like a dict.

        :param values: key-value pairs to update in database
        """
        for k, v in six.iteritems(values):
            # this should result in __setitem__ being called
            self[k] = v

    def get_value(self):
        """
        Retrieve the value of an instance of AppState

        :return: value of app state
        :rtype: varies
        """
        if self.dtype == INT_TYPE:
            return self.t_int
        if self.dtype == BOOL_TYPE:
            return self.t_bool
        if self.dtype == DATE_TYPE:
            return self.t_datetime
        if self.dtype == STR_TYPE:
            return self.t_string

        return None

    def set_value(self, value):

        """
        Sets the value of an instance of AppState

        :param value: the value of an app state instance
        :raise TypeError: if value type does not map to supported type
                          (string, int, boolean, datetime)
        """
        if value is None:
            dtype = NONE_TYPE
        else:
            dtype = type(value).__name__

            # handle the situations where we get some alternate type
            # that we can convert to a supported type
            if dtype == 'unicode':
                value = str(value)
                dtype = STR_TYPE
            if dtype == 'date':
                value = datetime.datetime.combine(value, datetime.time())
                dtype = DATE_TYPE

        # do not allow using multiple values for the same key unless it has
        # been reset to none first.
        if self.dtype and (self.dtype != NONE_TYPE) and (self.dtype != dtype):
            raise TypeError('Expecting type {0} for {1}: {2}'.format(
                self.dtype, self.name, dtype))

        if dtype in VAL_TYPES:
            self.dtype = dtype
            if dtype == INT_TYPE:
                self.t_int = value
            if dtype == BOOL_TYPE:
                self.t_bool = value
            if dtype == DATE_TYPE:
                self.t_datetime = value
            if dtype == STR_TYPE:
                self.t_string = value
            if dtype == NONE_TYPE:
                self.reset_value()
        else:
            raise TypeError(
                'Unsupported data type [{0}]; expecting {1}'.format(
                    dtype, VAL_TYPES))

    def reset_value(self):
        """
        Resets the value associated with AppState to empty
        """
        self.t_int = None
        self.t_bool = None
        self.t_datetime = None
        self.t_string = None

    def __repr__(self):
        return '<%s: %s=%s>' % (self.__class__.__name__,
                                self.name, self.get_value())


def verify_tables(engine):
    """
    Creates all the defined tables within the database

    :param engine: database engine instance
    """
    Base.metadata.create_all(engine)


def purge_all_tables(engine):
    """
    Drops all the defined tables within the database

    :param engine: database engine instance
    """
    Base.metadata.drop_all(engine)


class QueryTransformer(object):

    """
    Provides the ability to transform a query filter into database query in
    the sqlalchemy compliant manner.

    :param table: an instance of database table
    :type table: :class:`~seedbox.db.sqlalchemy.models.Base`
    :param query: an instance of database query
    :type query: :class:`~sqlalchemy.orm.query.Query`
    """
    operators = {'=': operator.eq,
                 '<': operator.lt,
                 '>': operator.gt,
                 '<=': operator.le,
                 '=<': operator.le,
                 '>=': operator.ge,
                 '=>': operator.ge,
                 '!=': operator.ne,
                 'in': lambda field_name, values: field_name.in_(values)
                 }

    complex_operators = {'or': sa.or_,
                         'and': sa.and_,
                         'not': sa.not_}

    def __init__(self, table, query):
        self.table = table
        self.query = query

    def _handle_complex_op(self, complex_op, nodes):
        op = self.complex_operators[complex_op]
        if op == sa.not_:
            nodes = [nodes]
        element_list = []
        for node in nodes:
            element = self._transform(node)
            element_list.append(element)
        return op(*element_list)

    def _handle_simple_op(self, simple_op, nodes):
        op = self.operators[simple_op]
        field_name = list(nodes.keys())[0]
        value = list(nodes.values())[0]
        return op(getattr(self.table, field_name), value)

    def _transform(self, sub_tree):
        op = list(sub_tree.keys())[0]
        nodes = list(sub_tree.values())[0]
        if op in self.complex_operators:
            return self._handle_complex_op(op, nodes)
        else:
            return self._handle_simple_op(op, nodes)

    def apply_filter(self, expression_tree):
        """
        Uses the filter to update the query

        :param expression_tree: query filter to apply
        :return: database query
        :rtype: :class:`~sqlalchemy.orm.query.Query`
        """
        condition = self._transform(expression_tree)
        self.query = self.query.filter(condition)
        return self.query
