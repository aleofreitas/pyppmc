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

"""Module containing application server methods.

"""

import csv
import notification
import os
import re
import requests
import security
import StringIO
import urllib
import urlparse
import util


class ServerNode:
    """Server node on application server.

    Parameters
    ----------
    name : str
        Server node name.
    params : dict of str : str, optional
        Server node parameters.

    Attributes
    ----------
    name : str
        Server node name.
    params : dict of str : str
        Server node parameters.

    """

    def __init__(self, name, params=None):
        self.name = name
        self.params = params


# noinspection SpellCheckingInspection
class Server:
    """The application server itself.

    Parameters
    ----------
    session : :obj:`Session`
        Current user session.

    Attributes
    ----------
    session : :obj:`Session`
        Current user session.
    server_nodes : :obj:`dict` of str : :obj:`ServerNode`
        Application server nodes.

    """
    SECURITY_LOGON_PAGE = '/itg/web/knta/global/Logon.jsp'
    """Relative URL to logon page."""
    SECURITY_LOGOUT_PAGE = '/itg/web/knta/global/Logout.jsp'
    """Relative URL to logout page."""
    SECURITY_HOME_PAGE = '/itg/web/knta/global/Home.jsp'
    """Relative URL to home page."""

    @property
    def base_url(self):
        """str: Application server base URL.

        """
        base_url = None
        for cookie in self.session.http_session.cookies:
            if cookie.name == 'JSESSIONID' and cookie.path == '/itg/':
                if cookie.secure:
                    protocol = 'https'
                    port = 443 if cookie.port is None else cookie.port
                else:
                    protocol = 'http'
                    port = 80 if cookie.port is None else cookie.port
                domain = cookie.domain
                base_url = '%s://%s:%d' % (protocol, domain, port)
        if base_url is not None:
            return base_url
        else:
            raise RuntimeError('Invalid session info. Not connected to PPM.')

    @property
    def public_key(self):
        """:obj:`elgamal.PublicKey`: Public key to be used for encryption.

        """
        if self._public_key is None:
            base_path = self.get_param('BASE_PATH')
            public_key_file = os.path.abspath(base_path + '/security/public_key.txt')
            if os.path.isfile(public_key_file):
                self._public_key = security.get_public_key(public_key_file)
            else:
                raise RuntimeError('Public key file not found.')

    @public_key.setter
    def public_key(self, value):
        self._public_key = value

    @property
    def private_key(self):
        """:obj:`elgamal.PrivateKey`: Private key to be used for decryption.

        """
        if self._private_key is None:
            base_path = self.get_param('BASE_PATH')
            private_key_file = os.path.abspath(base_path + '/security/private_key.txt')
            if os.path.isfile(private_key_file):
                self._public_key = security.get_private_key(private_key_file)
            else:
                raise RuntimeError('Private key file not found.')

    @private_key.setter
    def private_key(self, value):
        self._private_key = value

    def __init__(self, session):
        self.session = session
        self.server_nodes = {}
        self._load_config()
        self._public_key = None
        self._private_key = None

    @staticmethod
    def get_languages(url):
        """
        Get list of available languages.

        Get a list of all languages available to the user on the login page.

        Parameters
        ----------
        url : str
            Application server URL.

        Returns
        -------
        list of str
            List of all languages available on the login page.

        Raises
        ------
        RuntimeError
            If unable to connect to the logon page or to retrieve available languages from logon page.

        """
        logon_page = urlparse.urljoin(url, Server.SECURITY_LOGON_PAGE)
        response = requests.get(logon_page, verify=False)
        if response.status_code != requests.codes.ok:
            raise RuntimeError('Failed to connect to server.')

        content = response.content.decode('utf-8')
        langs = util.html.xpath(content, "//select[@id='field-language']/option/@value")
        if len(langs) == 0:
            raise RuntimeError('Unable to retrieve available languages.')
        return langs

    def encrypt(self, text):
        """Encrypts given text using PPM encoding functions.

        Parameters
        ----------
        text : str
            The text to be encrypted.

        Returns
        -------
        str
            The encrypted text

        """
        return security.encrypt(text, self.public_key)

    def download_file(self, filename):
        """Downloads a file from application server.

        Parameters
        ----------
        filename : str
            Relative path from BASE_PATH to the file.

        Returns
        -------
        str
            Contents of the given file.

        Notes
        -----
            Security files, such as public and private keys, are impossible to download.

        """
        params = {
            'download': '',
            'uri': filename
        }
        querystring = urllib.urlencode(params)
        file_url = urlparse.urljoin(self.base_url, '/itg/web/gwt/adminconsole/filebrowserdownload')
        file_url += '?' + querystring
        response = self.session.http_session.get(file_url, verify=False)
        result = response.content.encode('utf-8')
        return result

    def _load_config(self):
        """Loads server parameters from configuration file.

        """
        response = self.download_file('/server.conf')
        config = StringIO.StringIO(response)
        lines = config.readlines()
        config.close()

        params = {}
        node_params = {}
        is_node = False
        for line in lines:
            line = line.strip()
            if line == '@node':
                if not is_node:
                    node = ServerNode(params['KINTANA_SERVER_NAME'], params.copy())
                    self.server_nodes[params['KINTANA_SERVER_NAME']] = node
                    is_node = True
                else:
                    node = ServerNode(node_params['KINTANA_SERVER_NAME'], params.copy())
                    for param in node_params:
                        node.params[param] = node_params[param]
                    self.server_nodes[node_params['KINTANA_SERVER_NAME']] = node
                    node_params = {}
            else:
                pattern = '^com.kintana.core.server.(.+?)=(.*)$'
                m = re.match(pattern, line)
                if m is not None and len(m.groups()) == 2:
                    if not is_node:
                        params[m.groups()[0]] = m.groups()[1]
                    else:
                        node_params[m.groups()[0]] = m.groups()[1]
        if is_node:
            node = ServerNode(node_params['KINTANA_SERVER_NAME'], params.copy())
            for param in node_params:
                node.params[param] = node_params[param]
            self.server_nodes[node_params['KINTANA_SERVER_NAME']] = node
        else:
            node = ServerNode(params['KINTANA_SERVER_NAME'], params.copy())
            self.server_nodes[node_params['KINTANA_SERVER_NAME']] = node

    def get_param(self, param, server_node_name=None):
        """Returns the value of the given parameter.

        If `server_node_name` is not given, value for `param` is returned if `param` is not a node-specific parameter.
        If `server_node_name` is given, value for `param` is returned even if `param` is not a node-specific parameter.

        Parameters
        ----------
        param : str
            Name of the server parameter.
        server_node_name : str
            Name of the server node. Required for node-specific parameters.

        Returns
        -------
        str
            Value of the parameter

        Raises
        ------
        KeyError
            If `param` is an invalid server parameter or `server_node_name` is an invalid server node.
        RuntimeError
            If `param` is a node-specific parameter and `server_node_name` is not informed.

        """
        if server_node_name is None:
            values = []
            for server_node_name in self.server_nodes.keys():
                node = self.server_nodes[server_node_name]
                if param in node.params.keys():
                    values += [node.params[param]]
                else:
                    raise KeyError('Invalid parameter %s for server node name %s.' % (param, server_node_name))
            if len(set(values)) == 1:
                return values[0]
            else:
                raise RuntimeError('Node-specific parameter; server node name is required: %s.' % param)
        else:
            if server_node_name in self.server_nodes.keys():
                node = self.server_nodes[server_node_name]
            else:
                raise KeyError('Invalid server node name: %s.' % server_node_name)

            if param not in node.params.keys():
                raise KeyError('Invalid parameter: %s.' % param)
            else:
                return node.params[param]

    def send_notification(self, rcpt_to, rcpt_cc='', rcpt_bcc='', subject='', message='', mime_type='plain'):
        """Sends e-mail notifications.

        This method has the same behavior as the application server, sending e-mail notifications only when SMTP_SERVER
        parameter is set on the configuration file. If this parameter is not set, notifications are not set and no
        exceptions are raised.

        Parameters
        ----------
        rcpt_to : str
            Semicolon (;) separated list of e-mail addresses to be sent a notification via To field.
        rcpt_cc : str, optional
            Semicolon (;) separated list of e-mail addresses to be sent a notification via Cc field.
        rcpt_bcc : str, optional
            Semicolon (;) separated list of e-mail addresses to be sent a notification via Bcc field.
        subject : str, optional
            Message subject.
        message : str, optional
            Body of the message. Accepts HTML content.
        mime_type : str, optional
            Message MIME Type. Must be 'plain' or 'html'. Default is 'plain'

        """
        if self.get_param('SMTP_SERVER') != '':
            host = self.get_param('SMTP_SERVER')
            port = int(self.get_param('SMTP_PORT'))
            rcpt_from = self.get_param('EMAIL_NOTIFICATION_SENDER')
            username = ''
            password = ''
            try:
                username = self.get_param('SMTP_AUTH_USERNAME')
                password = self.get_param('SMTP_AUTH_PASSWORD')
                if security.is_encrypted(password):
                    password = security.decrypt(password, self.private_key)
            except KeyError:
                pass
            starttls = True if self.get_param('SMTP_USE_STARTTLS') == 'true' else False

            notification.send(host, port, rcpt_from, rcpt_to, username, password, starttls, rcpt_cc, rcpt_bcc,
                              subject, message, mime_type)

    # TODO Check ig current user has permission to run SQL Runner (HTTP response may give some information).
    def export_query(self, sql, fmt):
        """Exports the results of a SQL Query on the given format.

        `export_query` uses application server SQL Runner to run queries.

        Parameters
        ----------
        sql : str
            SQL query to run.
        fmt : str
            Format to export query results.

        Returns
        -------
        str
            Query results on the given format.

        """
        if sql is None or sql.strip() == '':
            raise ValueError('Invalid SQL query.')
        if fmt not in ['txt', 'csv']:
            raise ValueError("Invalid format: %s. Valid formats are 'txt' and csv.")
        data = {
            'sql': sql,
            'format': fmt
        }
        base_url = self.get_param('BASE_URL')
        url = urlparse.urljoin(base_url, '/itg/web/gwt/adminconsole/sqlrunnerexport')
        response = self.session.http_session.post(url, data, verify=False)
        result = response.content.decode(response.encoding).encode('utf-8')
        return result

    def run_query(self, sql):
        """Runs a SQL query and returns its results.

        Parameters
        ----------
        sql : str
            SQL query to run.

        Returns
        -------
        list of list of str
            List containing query results (rows and columns). The outer list contains all rows and the inner list
            contains all column values. `run_query` does not differentiate column types; all data is returned as str.

        """
        result = []
        exp = StringIO.StringIO(self.export_query(sql, 'csv'))
        reader = csv.reader(exp)
        entry = []
        for row in reader:
            if reader.line_num > 1:
                for column in row:
                    entry += [column]
                result += [row]
        exp.close()
        return result
