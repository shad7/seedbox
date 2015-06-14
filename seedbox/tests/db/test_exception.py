
from seedbox.db import exception
from seedbox.tests import test


class DbExceptionTest(test.BaseTestCase):

    def test_db_error(self):

        def gen_error(an_error):
            raise exception.DBError(an_error)

        err = self.assertRaises(exception.DBError,
                                gen_error,
                                ValueError)
        self.assertEqual(ValueError, err.inner_exception)

    def test_multiple_results_error(self):

        def gen_error(an_error):
            raise exception.MultipleResultsFound(an_error)

        err = self.assertRaises(exception.MultipleResultsFound,
                                gen_error,
                                RuntimeError)
        self.assertEqual(RuntimeError, err.inner_exception)

    def test_no_results_error(self):

        def gen_error(an_error):
            raise exception.NoResultFound(an_error)

        err = self.assertRaises(exception.NoResultFound,
                                gen_error,
                                RuntimeError)
        self.assertEqual(RuntimeError, err.inner_exception)

    def test_db_migration_error(self):

        def gen_error(an_error):
            raise exception.DbMigrationError(an_error)

        err = self.assertRaises(exception.DbMigrationError,
                                gen_error,
                                RuntimeError)
        self.assertEqual(RuntimeError, err.inner_exception)
