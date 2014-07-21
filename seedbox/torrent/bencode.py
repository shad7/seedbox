# The contents of this file are subject to the BitTorrent Open Source License
# Version 1.1 (the License).  You may not copy or use this file, in either
# source code or executable form, except in compliance with the License.  You
# may obtain a copy of the License at http://www.bittorrent.com/license/.
#
# Software distributed under the License is distributed on an AS IS basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied.  See the License
# for the specific language governing rights and limitations under the
# License.
# Written by Petru Paler
"""
Encodes and Decodes messages (http://en.wikipedia.org/wiki/Bencode)
updated to support Python 3
"""
import six


class BTFailure(Exception):
    """
    Represents any torrent failure
    """
    pass


def _decode_int(x, f):
    f += 1
    newf = x.index('e', f)
    n = int(x[f:newf])
    if x[f] == '-':
        if x[f + 1] == '0':
            raise ValueError
    elif x[f] == '0' and newf != f+1:
        raise ValueError
    return n, newf+1


def _decode_string(x, f):
    colon = x.index(':', f)
    n = int(x[f:colon])
    if x[f] == '0' and colon != f+1:
        raise ValueError
    colon += 1
    return x[colon:colon+n], colon+n


def _decode_list(x, f):
    r, f = [], f+1
    while x[f] != 'e':
        v, f = _decode_func[x[f]](x, f)
        r.append(v)
    return r, f + 1


def _decode_dict(x, f):
    r, f = {}, f+1
    while x[f] != 'e':
        k, f = _decode_string(x, f)
        r[k], f = _decode_func[x[f]](x, f)
    return r, f + 1


_decode_func = {
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
    :return: decoded message :rtype: dict
    :raise BTFailure: decoding failure
    """
    try:
        r, l = _decode_func[x[0]](x, 0)
    except (IndexError, KeyError, ValueError):
        raise BTFailure('not a valid bencoded string')
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


def _encode_bencached(x,r):
    r.append(x.bencoded)


def _encode_int(x, r):
    r.extend(('i', str(x), 'e'))


def _encode_bool(x, r):
    if x:
        _encode_int(1, r)
    else:
        _encode_int(0, r)


def _encode_string(x, r):
    r.extend((str(len(x)), ':', x))


def _encode_list(x, r):
    r.append('l')
    for i in x:
        _encode_func[type(i)](i, r)
    r.append('e')


def _encode_dict(x,r):
    r.append('d')
    ilist = x.items()
    ilist.sort()
    for k, v in ilist:
        r.extend((str(len(k)), ':', k))
        _encode_func[type(v)](v, r)
    r.append('e')


_encode_func = {
    Bencached: _encode_bencached,
    int: _encode_int,
    str: _encode_string,
    list: _encode_list,
    tuple: _encode_list,
    dict: _encode_dict,
    bool: _encode_bool,
    }
if six.PY2:
    _encode_func[long] = _encode_int
    _encode_func[unicode] = _encode_string


def bencode(x):
    """
    Public method for encoding message
    :param x: message
    :return: encoded string :rtype: string
    """
    r = []
    _encode_func[type(x)](x, r)
    return ''.join(r)
