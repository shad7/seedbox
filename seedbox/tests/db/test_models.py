import six
import testtools
from testtools import matchers

from seedbox.db import models
from seedbox.tests import test


class FakeModel(models.Model):

    def __init__(self, arg_a, arg_b, arg_c):
        models.Model.__init__(self,
                              arg_a=arg_a,
                              arg_b=arg_b,
                              arg_c=arg_c)


class DbModelTest(test.BaseTestCase):

    def test_base_model(self):
        fake = FakeModel.make_empty()
        self.assertIsInstance(fake, models.Model)

        _pk = FakeModel.pk_filter()
        self.assertIn(FakeModel.PK_NAME, _pk)

        other = FakeModel.make_empty()
        self.assertTrue(fake == other)

        self.assertEqual(len(fake.as_dict()), 3)
        self.assertEqual(len(list(fake.items())), 3)

        fake['arg_a'] = 1
        self.assertEqual(fake.arg_a, 1)

        val = fake['arg_a']
        self.assertEqual(val, 1)

        self.assertIn('arg_a', fake)
        self.assertNotIn('arg_z', fake)

        self.assertIsInstance(str(fake), six.string_types)

        self.assertThat(lambda: fake['arg_z'],
                        matchers.Raises(matchers.MatchesException(KeyError)))

        with testtools.ExpectedException(KeyError):
            fake['arg_z'] = 1

        fake.arg_b = other
        fake.arg_c = [other]
        self.assertEqual(len(fake.as_dict()), 3)

    def test_torrent_model(self):
        torrent = models.Torrent.make_empty()
        self.assertIsInstance(torrent, models.Torrent)

    def test_mediafile_model(self):
        mf = models.MediaFile.make_empty()
        self.assertIsInstance(mf, models.MediaFile)

    def test_appstate_model(self):
        appstate = models.AppState.make_empty()
        self.assertIsInstance(appstate, models.AppState)
