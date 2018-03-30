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

"""Package containing security related functions

Attributes
----------
CYPHER_TEXT_PATTERN : str
    Pattern of encrypted messages.
HASH_DELIMITER : str
    HASH delimiter used by PPM (#?#).
PASSWORD_DELIMITER : str
    Password delimiter used by PPM (#!#).
PRIVATE_KEY_HEADER : str
    Default content of the first line on the private key file.
PUBLIC_KEY_HEADER : str
    Default content of the first line on the public key file.

"""

import elgamal
import re

from elgamal import PrivateKey
from elgamal import PublicKey

CYPHER_TEXT_PATTERN = '^%s(.*)%s$'
HASH_DELIMITER = '#?#'
PASSWORD_DELIMITER = '#!#'
PRIVATE_KEY_HEADER = 'ElGamal Private Key'
PUBLIC_KEY_HEADER = 'ElGamal Public Key'


def get_public_key(public_key_file):
    """Returns a public key object.

    Parameters
    ----------
    public_key_file : str
        Path to the public_key_file

    Returns
    -------
    :obj:`PublicKey`
        Resulting public key object.

    """
    with open(public_key_file, 'r') as f:
        lines = f.readlines()
    if lines[0].rstrip() != PUBLIC_KEY_HEADER:
        raise IOError('Invalid file format.')
    bit_length = int(lines[1].rstrip())
    p = long(lines[2].rstrip(), 16)
    g = long(lines[3].rstrip(), 16)
    y = long(lines[4].rstrip(), 16)
    return PublicKey(bit_length, p, g, y)


def get_private_key(private_key_file):
    """Returns a private key object.

    Parameters
    ----------
    private_key_file : str
        Path to the private_key_file

    Returns
    -------
    :obj:`PrivateKey`
        Resulting private key object.

    """
    with open(private_key_file, 'r') as f:
        lines = f.readlines()
    if lines[0].rstrip() != PRIVATE_KEY_HEADER:
        raise IOError('Invalid file format.')
    bit_length = int(lines[1].rstrip())
    p = long(lines[2].rstrip(), 16)
    g = long(lines[3].rstrip(), 16)
    x = long(lines[4].rstrip(), 16)
    return PrivateKey(bit_length, p, g, x)


def is_encrypted(text):
    """Checks if a given text is encrypted or not.

     Result is given by checking if it is enclosed by `HASH_DELIMITER` or `PASSWORD_DELIMITER`.

    Parameters
    ----------
    text : str
        Text to be checked.

    Returns
    -------
    bool
        True if text is encrypted; False otherwise.

    """
    result = False
    mp = re.match(CYPHER_TEXT_PATTERN % (PASSWORD_DELIMITER, PASSWORD_DELIMITER), text)
    mh = re.match(CYPHER_TEXT_PATTERN % (HASH_DELIMITER, HASH_DELIMITER), text)
    if mp is not None or mh is not None:
        result = True
    return result


def get_cypher_text(text):
    """Returns the pure encrypted message.

    PPM signs if text is encrypted or not by enclosing it with `HASH_DELIMITER` or `PASSWORD_DELIMITER`. This method
    removes these delimiters returning the pure encrypted message.

    Parameters
    ----------
    text : str
        Encrypted message with or without delimiters.

    Returns
    -------
    str
        Encrypted message without delimiters.

    """
    mp = re.match(CYPHER_TEXT_PATTERN % (PASSWORD_DELIMITER, PASSWORD_DELIMITER), text)
    mh = re.match(CYPHER_TEXT_PATTERN % (HASH_DELIMITER, HASH_DELIMITER), text)
    if mp is not None:
        result = mp.groups()[0]
    elif mh is not None:
        result = mh.groups()[0]
    else:
        result = text
    return result


def encrypt(text, public_key):
    """Encrypts given text using given public key.

    Parameters
    ----------
    text : str
        Text to be encrypted.
    public_key
        Public key to encrypt.

    Returns
    -------
    str
        Encrypted text (without delimiters).

    """
    return elgamal.encrypt2(text, public_key)


def decrypt(text, private_key):
    """Decrypts given text using given private key.

    This methods handles if `text` is delimited (by `HASH_DELIMITER` or `PASSWORD_DELIMITER`) or not.

    Parameters
    ----------
    text : str
        Text to be decrypted.
    private_key
        Private key to decrypt.

    Returns
    -------
    str
        Decrypted text.

    """
    return elgamal.decrypt2(get_cypher_text(text), private_key)
