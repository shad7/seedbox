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
"""
Encodes and Decodes messages (http://en.wikipedia.org/wiki/Bencode)
updated to support Python 3
"""
import sys


try:
    unicode
except NameError:
    unicode = str

try:
    long
except NameError:
    long = int

if bytes == str:
    def _f(s, *args, **kwargs):
        return str(s)
    bytes = _f


class BTFailure(Exception):
    """
    Represents any torrent failure
    """
    pass


def bytes_index(s, pattern, start):
    """
    Returns the index of pattern within string starting at position start.

    :param s: byte string to search for pattern
    :type s: str
    :param pattern: pattern to search for within byte string
    :type pattern: str
    :param start: position/index within byte string to start scanning
    :type start: int
    :return: index of pattern within byte string
    :rtype: int
    """
    if sys.version_info[0] == 2:
        return s.index(pattern, start)

    assert len(pattern) == 1
    for i, e in enumerate(s[start:]):
        if e == ord(pattern):
            return i + start
    raise ValueError('substring not found')


def ord_(s):
    """
    Given a string representing one Unicode character, return an integer
    representing the Unicode code point of that character.

    :param s: string representing single unicode character
    :type s: str
    :return: integer representation of unicode character
    :rtype: int
    """
    if sys.version_info[0] == 3:
        return ord(s)
    return s


def chr_(s):
    """
    Return the string representing a character whose Unicode code point is
    the integer i.

    :param s: integer representation of unicode character
    :type s: int
    :return: string representation of unicode character
    :rtype: str
    """
    if sys.version_info[0] == 3:
        return chr(s)
    return s


def _decode_int(x, f):
    f += 1
    newf = bytes_index(x, 'e', f)
    n = int(x[f:newf])
    if x[f] == ord_('-'):
        if x[f + 1] == ord_('0'):
            raise ValueError
    elif x[f] == ord_('0') and newf != f+1:
        raise ValueError
    return n, newf+1


def _decode_string(x, f):
    colon = bytes_index(x, ':', f)
    n = int(x[f:colon])
    if x[f] == ord_('0') and colon != f+1:
        raise ValueError
    colon += 1
    return x[colon:colon+n], colon+n


def _decode_list(x, f):
    r, f = [], f+1
    while x[f] != ord_('e'):
        v, f = decode_func[chr_(x[f])](x, f)
        r.append(v)
    return r, f + 1


def _decode_dict(x, f):
    r, f = {}, f+1
    while x[f] != ord_('e'):
        k, f = _decode_string(x, f)
        r[k], f = decode_func[chr_(x[f])](x, f)
    return r, f + 1


decode_func = {
    'l': _decode_list,
    'd': _decode_dict,
    'i': _decode_int,
    '0': _decode_string,
    '1': _decode_string,
    '2': _decode_string,
    '3': _decode_string,
    '4': _decode_string,
    '5': _decode_string,
    '6': _decode_string,
    '7': _decode_string,
    '8': _decode_string,
    '9': _decode_string,
    }


def bdecode(x):
    """
    Public method for decoding a message

    :param x: message to decode
    :return: decoded message
    :rtype: dict
    :raise BTFailure: decoding failure
    """
    try:
        r, l = decode_func[chr_(x[0])](x, 0)
    except (IndexError, KeyError, TypeError, ValueError) as err:
        raise BTFailure('not a valid bencoded string; error details ({0'
                        '})'.format(err))
    if l != len(x):
        raise BTFailure('invalid bencoded value (data after valid prefix)')
    return r


class Bencached(object):
    """
    Cached bencode class
    """

    __slots__ = ['bencoded']

    def __init__(self, s):
        self.bencoded = s


def _encode_bencached(x, r):
    r.append(x.bencoded)


def _encode_int(x, r):
    r.append(b'i')
    r.append(bytes(str(x), 'ascii'))
    r.append(b'e')


def _encode_bool(x, r):
    if x:
        _encode_int(1, r)
    else:
        _encode_int(0, r)


def _encode_string(x, r):
    r.extend((bytes(str(len(x)), 'ascii'), b':', x))


def _encode_list(x, r):
    r.append(b'l')
    for i in x:
        encode_func[type(i)](i, r)
    r.append(b'e')


def _encode_dict(x, r):
    r.append(b'd')
    ilist = list(x.items())
    ilist.sort()
    for k, v in ilist:
        r.extend((bytes(str(len(k)), 'ascii'), b':', k))
        encode_func[type(v)](v, r)
    r.append(b'e')


encode_func = {
    Bencached: _encode_bencached,
    int: _encode_int,
    long: _encode_int,
    str: _encode_string,
    bytes: _encode_string,
    unicode: _encode_string,
    list: _encode_list,
    tuple: _encode_list,
    dict: _encode_dict,
    bool: _encode_bool,
    }


def bencode(x):
    """
    Public method for encoding message

    :param x: message
    :return: encoded string
    :rtype: string
    """
    r = []
    encode_func[type(x)](x, r)
    return b''.join(r)
