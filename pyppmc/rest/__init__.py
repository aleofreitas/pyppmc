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

"""Package rest

Package for RESTful web services operations.

Attributes
----------
ISO_DATE_FORMAT : str
    ISO 8601 date format

"""

__all__ = ['dm', 'tm']

import datetime
import httplib
import requests
import urlparse

ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'


def iso_to_datetime(value):
    """Converts an ISO 8601 date string to a datetime object.

    Parameters
    ----------
    value : str
        ISO 8601 date string to convert.

    Returns
    -------
    :[obj]:`datetime`
        Resulting date object.

    """
    return datetime.datetime.strptime(value[:19], ISO_DATE_FORMAT)


def datetime_to_iso(value):
    """Converts a datetime object to an ISO 8601 date string.

    Parameters
    ----------
    value : datetime
        Datetime object to convert.

    Returns
    -------
    str
        ISO 8601 date string.

    """
    tz = '%+03d:00' % (int(round((datetime.datetime.now() - datetime.datetime.utcnow()).total_seconds())) / 3600)
    return datetime.datetime.strftime(value, ISO_DATE_FORMAT) + '.000' + tz


def call_operation(http_session, method, path, data=None, params=None, message_type='xml'):
    """Calls a REST service operation.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    method : str
        HTTP method. Valid values are GET and POST.
    path : str
        Operation path.
    data : dict of str : str, optional
        Data to be consumed by the operation.
    params : dict of str : str, optional
        Query parameters to passed to the operation.
    message_type : str, optional
        Message type to use. Valid values are xml and json.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    Raises
    ------
    ValueError
        If an invalid method is passed.
        If an invalid message type is passed.
    HTTPError
        If HTTP response status code is not equal to 200.

    """
    base_url = ''
    for cookie in http_session.cookies:
        if cookie.name == 'JSESSIONID' and cookie.path == '/itg/':
            if cookie.secure:
                protocol = 'https'
                port = 443 if cookie.port is None else cookie.port
            else:
                protocol = 'http'
                port = 80 if cookie.port is None else cookie.port
            domain = cookie.domain
            base_url = '%s://%s:%d/' % (protocol, domain, port)
            break

    if message_type == 'xml':
        headers = {'Content-Type': 'application/xml; charset=utf-8'}
    elif message_type == 'json':
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        params = {'alt': 'application/json'} if not params else params.update({'alt': 'application/json'})
    else:
        raise ValueError('Invalid message type: %s. Valid values are xml and json.' % message_type)
    uri = urlparse.urljoin(base_url, path)
    if method == 'GET':
        response = http_session.get(uri, data=data, verify=False, headers=headers, params=params)
        if response.status_code == requests.codes.ok:
            return response
        else:
            raise requests.HTTPError('%d %s' % (response.status_code, httplib.responses[response.status_code]))
    elif method == 'POST':
        response = http_session.post(uri, data=data, verify=False, headers=headers, params=params)
        if response.status_code == requests.codes.ok:
            return response
        else:
            raise requests.HTTPError('%d %s' % (response.status_code, httplib.responses[response.status_code]))
    elif method == 'PUT':
        response = http_session.post(uri, data=data, verify=False, headers=headers, params=params)
        if response.status_code == requests.codes.ok:
            return response
        else:
            raise requests.HTTPError('%d %s' % (response.status_code, httplib.responses[response.status_code]))
    elif method == 'DELETE':
        response = http_session.delete(uri, data=data, verify=False, headers=headers, params=params)
        if response.status_code == requests.codes.no_content:
            return response
        else:
            raise requests.HTTPError('%d %s' % (response.status_code, httplib.responses[response.status_code]))
    else:
        raise ValueError('Invalid HTTP method: %s' % method)
