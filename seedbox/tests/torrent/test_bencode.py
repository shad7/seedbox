# Copyright (c) 2012-2013 BitTorrent, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from seedbox.tests import test
from seedbox.torrent import bencode


class KnownValues(test.BaseTestCase):
    """ * example values partially taken from http://en.wikipedia.org/wiki/Bencode
        * test case inspired by Mark Pilgrim's examples:
            http://diveintopython.org/unit_testing/romantest.html
    """
    knownValues = (
        (0, b'i0e'),
        (1, b'i1e'),
        (10, b'i10e'),
        (42, b'i42e'),
        (-42, b'i-42e'),
        (True, b'i1e'),
        (False, b'i0e'),
        (b'spam', b'4:spam'),
        (b'parrot sketch', b'13:parrot sketch'),
        ([b'parrot sketch', 42], b'l13:parrot sketchi42ee'),
        ({b'foo': 42,
          b'bar': b'spam'},
         b'd3:bar4:spam3:fooi42ee'),
    )

    def test_bencode_known_values(self):
        """bencode should give known result with known input"""
        for plain, encoded in self.knownValues:
            result = bencode.bencode(plain)
            self.assertEqual(encoded, result)

    def test_bdecode_known_values(self):
        """bdecode should give known result with known input"""
        for plain, encoded in self.knownValues:
            result = bencode.bdecode(encoded)
            self.assertEqual(plain, result)

    def test_roundtrip_encoded(self):
        """ consecutive calls to bdecode and bencode should deliver the original
            data again
        """
        for plain, encoded in self.knownValues:
            result = bencode.bdecode(encoded)
            self.assertEqual(encoded, bencode.bencode(result))

    def test_roundtrip_decoded(self):
        """ consecutive calls to bencode and bdecode should deliver the original
            data again
        """
        for plain, encoded in self.knownValues:
            result = bencode.bencode(plain)
            self.assertEqual(plain, bencode.bdecode(result))


class IllegaleValues(test.BaseTestCase):
    """ handling of illegal values"""

    def test_nonstrings_raise_illegal_input_for_decode(self):
        """ non-strings should raise an exception. """
        self.assertRaises(bencode.BTFailure, bencode.bdecode, [0])
        self.assertRaises(bencode.BTFailure, bencode.bdecode, None)
        self.assertRaises(bencode.BTFailure, bencode.bdecode, [1, 2])
        self.assertRaises(bencode.BTFailure, bencode.bdecode, {b'foo': b'bar'})

    def test_raise_illegal_input_for_decode(self):
        """Illegally formatted strings should raise an exception when
        decoded."""
        self.assertRaises(bencode.BTFailure, bencode.bdecode, b"foo")
        self.assertRaises(bencode.BTFailure, bencode.bdecode, b"x:foo")
        self.assertRaises(bencode.BTFailure, bencode.bdecode, b"x42e")


class Dictionaries(test.BaseTestCase):
    """ handling of dictionaries """

    def test_sorted_keys_for_dicts(self):
        """ the keys of a dictionary must be sorted before encoded. """
        adict = {b'zoo': 42, b'bar': b'spam'}
        encoded_dict = bencode.bencode(adict)
        self.assertTrue(
            encoded_dict.index(b'zoo') > encoded_dict.index(b'bar'))

    def test_nested_dictionary(self):
        """ tests for handling of nested dicts"""
        adict = {b'foo': 42, b'bar': {b'sketch': b'parrot', b'foobar': 23}}
        encoded_dict = bencode.bencode(adict)
        self.assertEqual(encoded_dict,
                         b"d3:bard6:foobari23e6:sketch6:parrote3:fooi42ee")
