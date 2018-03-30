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

"""A Python module to provide access to a Micro Focus™ Project and Portfolio Management Center server.

# """

__all__ = ['foundation', 'notification', 'request', 'server', 'session']

from server import Server
from session import Session


def get_languages(url):
    """Returns a list of available languages.

    Returns a list of all languages available to the user on the login page.

    Parameters
    ----------
    url : str
        Application server URL.

    Returns
    -------
    list of str
        List of all languages available on the login page.

    """
    return Server.get_languages(url)


def logon(url, username, password, language):
    """Logs onto the application server.

    Parameters
    ----------
    url : str
        Application server URL.
    username : str
        Username to log in.
    password : str
        Password to log in.
    language : str
        Language used by the user. Must be one of the languages returned by get_languages().

    Returns
    -------
    :obj:`Session`
        New user session on application server.

    """
    return Session(url, username, password, language)
