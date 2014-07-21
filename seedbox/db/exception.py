"""
Database Exception definition classes
"""
import six


class DBError(Exception):
    """Wraps an implementation specific exception."""
    def __init__(self, inner_exception=None):
        self.inner_exception = inner_exception
        super(DBError, self).__init__(six.text_type(inner_exception))


class MultipleResultsFound(DBError):
    """Represents when Multiple results found when searching by unique id"""
    pass


class NoResultFound(DBError):
    """Represents when No results found when fetching by unique id"""
    pass


class DbMigrationError(DBError):
    """Wraps migration specific exception."""
    def __init__(self, message=None):
        super(DbMigrationError, self).__init__(message)
