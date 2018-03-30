# -*- coding: utf-8 -*-
# Copyright 2018 Alexandre Freitas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing encryption methods.

The implementation of the methods in this module is based on the respective PPM methods.

Attributes
----------
    charset : str
        String containing all valid Base66 encoding characters.
    radix_map : str
        String containing all valid Base85 (Ascii85) encoding characters.

"""

import fractions
import random
import struct
import sys

from binascii import unhexlify

charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789~_-+'
radix_map = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`~@$^&*()_+=-{}|:<>./? "
sys.setrecursionlimit(1000000)
random.randrange(-sys.maxint - 1, sys.maxint)


class PublicKey:
    """An El Gamal public key.

    Parameters
    ----------
        bit_length : int
            Bit length of the key. One byte has 8 bits, so keys will be `bit_length`/8 characters length. Default bit
            length in PPM is 600, which results on 75 bytes (chars) length keys.
        p: int
            ElGamal algorithm modulus.
        g : int
            ElGamal algorithm generator.
        y: int
            ElGamal public key

    Attributes
    ----------
        bit_length : int
            Bit length of the key. One byte has 8 bits, so keys will be `bit_length`/8 characters length. Default bit
            length in PPM is 600, which results on 75 bytes (chars) length keys.
        p: int
            ElGamal algorithm modulus.
        g : int
            ElGamal algorithm generator.
        y: int
            ElGamal public key

    """

    def __init__(self, bit_length, p, g, y):
        if p is None:
            raise TypeError('p cannot be NoneType.')
        if g is None:
            raise TypeError('g cannot be NoneType.')
        if y is None:
            raise TypeError('y cannot be NoneType.')
        if bit_length < p.bit_length():
            raise ValueError('Public key bit length cannot be less than p bit length.')
        self.bit_length = bit_length
        self.p = p
        self.g = g
        self.y = y


class PrivateKey:
    """An El Gamal private key.

    Parameters
    ----------
        bit_length : int
            Bit length of the key. One byte has 8 bits, so keys will be `bit_length`/8 characters length. Default bit
            length in PPM is 600, which results on 75 bytes (chars) length keys.
        p: int
            ElGamal algorithm modulus.
        g : int
            ElGamal algorithm generator.
        x: int
            ElGamal private key

    Attributes
    ----------
        bit_length : int
            Bit length of the key. One byte has 8 bits, so keys will be `bit_length`/8 characters length. Default bit
            length in PPM is 600, which results on 75 bytes (chars) length keys.
        p: int
            ElGamal algorithm modulus.
        g : int
            ElGamal algorithm generator.
        x: int
            ElGamal private key

    """

    def __init__(self, bit_length, p, g, x):
        if p is None:
            raise TypeError('p cannot be NoneType.')
        if g is None:
            raise TypeError('g cannot be NoneType.')
        if x is None:
            raise TypeError('x cannot be NoneType.')
        if bit_length < p.bit_length():
            raise ValueError('Private key bit length cannot be less than p bit length.')
        self.bit_length = bit_length
        self.p = p
        self.g = g
        self.x = x


def xgcd(a, b):
    """Calculates the extended greatest common divisor for two numbers (extended Euclidean algorithm).

    Parameters
    ----------
    a : int
        First number.
    b : int
        Second number.

    Returns
    -------
    int:
        The extended greatest common divisor for the two given numbers.

    """
    if a == 0:
        return b, 0, 1
    else:
        g, x, y = xgcd(b % a, a)
        return g, y - (b // a) * x, x


def mulinv(b, m):
    """Calculates the modular inverse of b(modulo m).

    Modular inverse is an application of the extended Euclidean algorithm.

    Parameters
    ----------
    b : int
        Integer number.
    m : int
        Modulus of the operation.

    Returns
    -------
    int
        The modular inverse for b(modulo m).

    """
    g, x, _ = xgcd(b, m)
    if g == 1:
        return x % m


def long_to_bytes(value):
    """Converts a number into a byte array.

    Number is converted to Big Endian format.

    Parameters
    ----------
    value : long
        Number to be converted.

    Returns
    -------
    list of str
        List containing converted bytes.

    """
    width = value.bit_length()
    width += 8 - ((width % 8) or 8)
    fmt = '%%0%dx' % (width // 4)
    s = unhexlify(fmt % value)
    return s


# noinspection PyTypeChecker
def bytes_to_long(barray):
    """Converts a byte array into a number.

    Parameters
    ----------
    barray : list of str
        Byte array to convert.

    Returns
    -------
    long:
        Converted number.

    """
    result = 0L
    for i in range(0, len(barray)):
        result = result << 8
        result += barray[i]
    return result


def divrem(x, y):
    """A simple implementation of the remainder of a division.

    Parameters
    ----------
    x : int
        Dividend or numerator.
    y : int
        Divisor or denominator.

    Returns
    -------
    int
        Remainder of `x`/`y`.

    """
    signx = 1 if x >= 0 else -1
    x = abs(x)
    y = abs(y)
    q = int(x / y)
    r = x - (q * y)
    return signx * r


def long_to_radix85(b):
    """Encodes a number into a Base85 string.

    Parameters
    ----------
    b : int
        Number to convert.

    Returns
    -------
    str
        Number encoded to string.

    """
    radix = len(radix_map)
    buf = ''
    while b.bit_length() != 0:
        d = divrem(b, radix)
        buf = radix_map[d] + buf
        b /= radix
    return buf


def radix85_to_long(s):
    """Decodes a Base85 string into a number.

    Parameters
    ----------
    s : str
        The encoded string.

    Returns
    -------
    int
        String decoded to number.

    """
    b = 0
    r85 = 85
    for i in range(0, len(s)):
        n = radix_map.find(s[i])
        if n < 0:
            raise RuntimeError('Not a radix85 character: %s.' % s[i])
        b = (b * r85) + n
    return b


def findk(p):
    """Returns ElGamal secret key.

    k is a secret number chosen randomly in the closed range(1, p-2), where p is ElGamal algorithm modulus.

    Parameters
    ----------
    p : int
        ElGamal algorithm modulus.

    Returns
    -------
    int
        ElGamal secret key k.

    """
    p_minus_one = p - 1
    while True:
        k = random.getrandbits(p.bit_length())
        if not (k & 1):
            k += 1
        if fractions.gcd(k, p_minus_one) == 1:
            break
    return k


def encrypt_block(encoded_bytes, offset, public_key):
    """Encrypts given encoded bytes using given public key.

    Parameters
    ----------
    encoded_bytes : list of str
        Encoded byte array.
    offset : int
        Offset to start encryption.
    public_key : :obj:`PublicKey`
        ElGamal public key to use.

    Returns
    -------
    str
        Encrypted text.

    """
    block = encoded_bytes[offset:]
    t = bytes_to_long(block)
    k = findk(public_key.p)
    a = pow(public_key.g, k, public_key.p)
    b = divrem(pow(public_key.y, k, public_key.p) * t, public_key.p)
    return long_to_radix85(a) + ',' + long_to_radix85(b)


def decrypt_block(encrypted_text, length, private_key):
    """Decrypts given encrypted text using given private key.

    Parameters
    ----------
    encrypted_text : str
        Text to decrypt.
    length : int
        Length of the block to decrypt.
    private_key : :obj:`PrivateKey`
        ElGamal private key to use.

    Returns
    -------
    list of str
        Decrypted byte array.

    """
    tokens = encrypted_text.split(',')
    a = radix85_to_long(tokens[0])
    b = radix85_to_long(tokens[1])

    x = private_key.x
    p = private_key.p
    d = divrem((b * (mulinv(pow(a, x, p), p))), p)
    barray = long_to_bytes(d)

    if len(barray) > length:
        block = barray[-length:]
    else:
        block = [0] * (length - len(barray))
        block += barray[:]
    return block


def twos_comp(n, b):
    """Calculates the two's complement of a given number.

    Parameters
    ----------
    n : int
        Number to calculate its two's complement.
    b : int
        Number of bits.

    Examples
    --------
    Given `bits` = 3 and `n` = 4 (0b100), twos_comp(4, 3) equals -4 (0b100).
    Given `bits` = 4 and `n` = 4 (0b0100), twos_comp(4, 4) equals 4 (0b0100).

    Returns
    -------
    int
        Two's complement of `n` with `b` bits.

    """
    if (n & (1 << (b - 1))) != 0:
        n = n - (1 << b)
    return n


# noinspection PyTypeChecker
def utf_to_str(barray):
    """Decodes an UTF byte array into a string

    Parameters
    ----------
    barray : list of str
        Byte array to decode.

    Returns
    -------
    str
        Decoded string.

    """
    buf = ''
    padding = ord(barray[-1])
    for i in range(0, len(barray) - 1):
        padding = divrem((padding - ord(barray[i]) - 256), 256)
    if padding < 0:
        padding += 256
    i = 0
    data = barray[0: len(barray) - padding]
    while i < len(data):
        c = struct.unpack('B', data[i])[0]
        i += 1
        if c < 0:
            break
        if (c >> 4) in range(0, 8):
            buf += chr(c)
        elif (c >> 4) in range(12, 14):
            char2 = struct.unpack('B', data[i])[0]
            i += 1
            if (char2 & 0xC0) != 128:
                raise RuntimeError('Bad UTF.')
            buf += chr(((c & 0x1F) << 6 | char2 & 0x3F))
        elif (c >> 4) == 14:
            char2 = struct.unpack('B', data[i])[0]
            char3 = struct.unpack('B', data[i + 1])[0]
            i += 2
            if ((char2 & 0xC0) != 128) or ((char3 & 0xC0) != 128):
                raise RuntimeError('Bad UTF.')
            buf += chr(((c & 0xF) << 12 | (char2 & 0x3F) << 6 | (char3 & 0x3F) << 0))
        else:
            raise RuntimeError('Bad UTF.')
    return ''.join(buf)


def str_to_utf(s, block_length):
    """Encodes a string into a UTF byte array.

    Parameters
    ----------
    s : str
        String to convert
    block_length : int
        Length of the block to encode.

    Returns
    -------
    list of str
        Encoded byte array.

    """
    b = []
    for i in range(0, len(s)):
        c = s[i]
        if '\001' <= c <= '':
            b += [ord(c)]
        elif c > '?':
            b += [0xE0 | ord(c) >> ord('\f') & 0xF]
            b += [0x80 | ord(c) >> ord('\006') & 0x3F]
            b += [0x80 | ord(c) >> ord('\000') & 0x3F]
        else:
            b += [0xC0 | ord(c) >> ord('\006') & 0x1F]
            b += [0x80 | ord(c) >> ord('\000') & 0x3F]

    padding = block_length - divrem(len(b), block_length)
    if padding == 0:
        padding = block_length

    barray = b[:] + ([0] * (block_length - len(b)))
    for i in range(0, len(b)):
        padding = divrem((padding + b[i] + 256), 256)
        barray[-1] = twos_comp(padding, 8)
    return barray


def encrypt(encoded_text, public_key):
    """Encrypts given encoded text using given public key.

    Parameters
    ----------
    encoded_text : str
        Encoded text to encrypt.
    public_key : :[obj]:`PublicKey`
        ElGamal public key to use.

    Returns
    -------
    str
        Encrypted text.

    """
    result = ''
    if encoded_text is not None and len(encoded_text) > 0:
        block_length = min(127, public_key.bit_length / 8)
        plain_bytes = str_to_utf(encoded_text, block_length)
        for i in range(0, len(plain_bytes), block_length):
            if i != 0:
                result += ';'
            result += encrypt_block(plain_bytes, i, public_key)
    return result


def decrypt(encrypted_text, private_key):
    """Decrypts give encrypted text using given private key.

    Parameters
    ----------
    encrypted_text : str
        Text to decrypt.
    private_key : :[obj]:`PrivateKey`
        ElGamal private key to use.

    Returns
    -------
    str
        Encoded text.

    """
    result = ''
    if encrypted_text is not None and len(encrypted_text) > 0:
        block_length = min(127, private_key.bit_length / 8)
        # noinspection SpellCheckingInspection
        byteout = []
        for token in encrypted_text.split(';'):
            block = decrypt_block(token, block_length, private_key)
            byteout += block
        result = utf_to_str(byteout)
    return result


def next_positive_random(modulus):
    """Calculates a positive random number in the range(0, modulus - 1).

    Parameters
    ----------
    modulus : int
        Modulus of the operation.

    Returns
    -------
    int
        New positive random integer.

    """
    rn = random.randint(0, sys.maxint)
    return divrem(abs(rn), modulus)


def encode(plain_text):
    """Encodes given plain text.

    Parameters
    ----------
    plain_text : str
        Plain text to encode.

    Returns
    -------
    str
        Encoded string.

    """
    prefix_length = next_positive_random(2) + 4
    buf = ''
    for i in range(0, prefix_length):
        buf += charset[next_positive_random(len(charset))]
    return buf + ' ' + plain_text


def decode(encoded_text):
    """Decodes given encoded text.

    Parameters
    ----------
    encoded_text : str
        Text to decode.

    Returns
    -------
    str
        Decoded string.

    """
    index = encoded_text.find(' ')
    if index < 0:
        raise RuntimeError("Text doesn't appear to be encoded or there is an encryption key mismatch.")
    return encoded_text[index + 1:]


def encrypt2(plain_text, public_key):
    """Encrypts given plain text using given public key.

    Parameters
    ----------
    plain_text : str
        Plain text to encrypt.
    public_key : :[obj]:`PublicKey`
        ElGamal public key to use.

    Returns
    -------
    str
        Encrypted text.

    """
    result = ''
    if plain_text is not None and len(plain_text) > 0:
        result = encrypt(encode(plain_text), public_key)
    return result


def decrypt2(encrypted_text, private_key):
    """Decrypts given encrypted text using given private key.

    Parameters
    ----------
    encrypted_text : str
        Text to decrypt.
    private_key : :[obj]:`PrivateKey`
        ElGamal private key to use.

    Returns
    -------
    str
        Decrypted text.

    """
    result = ''
    if encrypted_text is not None and len(encrypted_text) > 0:
        result = decode(decrypt(encrypted_text, private_key))
    return result
