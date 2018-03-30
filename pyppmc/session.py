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

# TODO Implement authentication over HTTPS.

"""session.py

Module for user session methods.

"""

import requests
import urlparse
import util

from server import Server


class Session:
    """User session on the application server.

    Session objects are the way to access all application server features.

    Parameters
    ----------
    url : str
        Application server URL.
    username : str
        Username to log in.
    password : str
        Password to log in.
    language : str
        Language used by the user.

    Attributes
    ----------
    url : str
        Application server URL.
    username : str
        Username to log in.
    password : str
        Password to log in.
    language : str
        Language used by the user.
    db_con : :[obj]:`Connection`
        Connection to application database.

    Raises
    ------
    RuntimeError
        If unable to connect to the logon page or to logon (invalid `username` or `password`).
    ValueError
        If `language` is invalid.

    """

    def __init__(self, url, username, password, language):
        self.url = url
        self.username = username
        self.password = password
        self.language = language
        http_session = requests.Session()

        # Required to call SOAP web services
        http_session.auth = (self.username, self.password)
        logon_page = urlparse.urljoin(self.url, Server.SECURITY_LOGON_PAGE)
        response = http_session.get(logon_page, verify=False)
        if response.status_code != requests.codes.ok:
            raise RuntimeError('Failed to connect to server.')

        content = response.content.decode('utf-8')
        langs = util.html.xpath(content, "//select[@id='field-language']/option/@value")
        if self.language is None or self.language not in langs:
            raise ValueError(
                'Invalid language: %s. For a list of installed languages check get_languages().' % self.language)

        key = util.html.xpath(content, "//input[@name='WebSessionKey']/@value")[0]

        data = {
            'USERNAME': self.username,
            'PASSWORD': self.password,
            'nls_language': self.language,
            'WebSessionKey': key
        }
        home_page = urlparse.urljoin(self.url, Server.SECURITY_HOME_PAGE)
        response = http_session.post(home_page, data=data, verify=False)
        if len(response.cookies) == 0:
            raise RuntimeError('Invalid username or password.')
        self.http_session = http_session

        # TODO Implement logic to get information about the authenticated user.
        self.auth_user = None

        # TODO Implement logic to build a database connection using default Server properties.
        self.db_con = None

    def __del__(self):
        """Destroys the current user session on application server.

        """
        if len(self.http_session.cookies) > 0:
            logout_page = urlparse.urljoin(self.url, Server.SECURITY_LOGOUT_PAGE)
            self.http_session.get(logout_page, verify=False)
