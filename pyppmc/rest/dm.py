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

"""dm.py

Module containing Demand Management RESTful web services operations.

Attributes
----------
REQUESTS_PATH : str
    Path to requests collection.
REQUEST_TYPES_PATH : str
    Path to requestTypes collection.

"""

import datetime
import json
import rest

from request import Request

REQUESTS_PATH = '/itg/rest/dm/requests'
REQUEST_TYPES_PATH = '/itg/rest/dm/requestTypes'

# TODO Rewrite method to return a list of request types.
def get_enabled_request_types(http_session):
    """Returns PPM enabled request types.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = REQUEST_TYPES_PATH
    return rest.call_operation(http_session, 'GET', path, message_type='json')


# TODO Rewrite method to return a request type object.
def get_request_type(http_session, request_type_id):
    """Returns details about the given request type.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    request_type_id : int
        Request type id.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = '%s/%d' % (REQUEST_TYPES_PATH, request_type_id)
    return rest.call_operation(http_session, 'GET', path, message_type='json')


# TODO Rewrite method to return a list of requests.
def get_requests(http_session, request_type_id):
    """Returns requests with the given request_type.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    request_type_id : int
        Request type id.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = '%s/%d/requests' % (REQUEST_TYPES_PATH, request_type_id)
    return rest.call_operation(http_session, 'GET', path, message_type='json')


def get_request(http_session, request_id):
    """Returns the given request.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    request_id : int
        Request id.

    Returns
    -------
    :[obj]:`Request`
        Request object containing its data.

    """
    path = '%s/%d' % (REQUESTS_PATH, request_id)
    response = rest.call_operation(http_session, 'GET', path, message_type='json')
    result = json.loads(response.content)
    request = Request()
    for field in result['ns2:request']['fields']['field']:
        if 'stringValue' in field:
            request.fields[field['name']] = field['stringValue']
        elif 'dateValue' in field:
            request.fields[field['name']] = rest.iso_to_datetime(field['dateValue'])
    return request


def update_request(http_session, request):
    """Creates or updates a request.

    Request is updated if name REQ.REQUEST_ID is present, otherwise request is created.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    request : :[obj]:`Request`
        Request data.

    Returns
    -------
    :[obj]:`Request`
        Request object containing its data.

    Notes
    -----
        Although this method accepts fields with their hidden/visible (P/VP) identification, it always returns name
        names without this identification. It also returns only the visible (VP) fields.

    """
    request_id = request.tokens['REQ.REQUEST_ID'] if 'REQ.REQUEST_ID' in request.tokens else '0'
    description = request.tokens['REQ.DESCRIPTION'] if 'REQ.DESCRIPTION' in request.tokens else ''
    request_type = request.tokens['REQ.REQUEST_TYPE_NAME'] if 'REQ.REQUEST_TYPE_NAME' in request.tokens else ''

    payload = {
        'request': {
            'description': description,
            'requestType': request_type
        }
    }

    if int(request_id) > 0:
        payload['request']['request_id'] = request_id

    field = []
    for token in request.tokens.keys():
        value = request.tokens[token]
        if isinstance(value, datetime.datetime):
            field += [{
                'name': token,
                'dateValue': rest.datetime_to_iso(value)
            }]
        else:
            field += [{
                'name': token,
                'stringValue': value
            }]

    payload['request']['fields'] = {'field': field}
    path = REQUESTS_PATH
    response = rest.call_operation(http_session, 'POST', path, data=json.dumps(payload), message_type='json')
    result = json.loads(response.content)
    request.tokens = dict()
    for field in result['ns2:request']['fields']['field']:
        if 'stringValue' in field:
            request.tokens[field['name']] = field['stringValue']
        elif 'dateValue' in field:
            request.tokens[field['name']] = rest.iso_to_datetime(field['dateValue'])
    return request


def delete_request(http_session, request_id):
    """Deletes the given request.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    request_id : int
        Request to delete.

    Returns
    -------
    None

    """
    path = '%s/%d' % (REQUESTS_PATH, request_id)
    rest.call_operation(http_session, 'DELETE', path, message_type='json')


class RequestRest:
    """Request persistence class based on PPM RESTful Web Services.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        A request.Session session object.

    """

    def __init__(self, http_session):
        self.http_session = http_session

    def get(self, request_id):
        """Returns details for the given request.

        Parameters
        ----------
        request_id : int
            ID of the request.

        Returns
        -------
        :[obj]:`Request`
            Object containing request data.

        """
        request = get_request(self.http_session, request_id)
        request.persister = self
        return request

    def save(self, request):
        """Saves the request.

        If REQ.REQUEST_ID name is present on request object, then the given request is updated.
        Otherwise a new request is created.

        Parameters
        ----------
        request : :[obj]:`Request`
            Request object containing the data to persist.

        Returns
        -------
        :[obj]:`Request`
            The new or updated request.

        """
        return update_request(self.http_session, request)

    def delete(self, request):
        """Deletes the request.

        Parameters
        ----------
        request : :[obj]:`Request`
            Request object to delete.

        Returns
        -------
        :[obj]:`Request`
            Request object without name REQ.REQUEST_ID

        Raises
        ------
        RuntimeError
            If REQ.REQUEST_ID name exists and operation returns 0 deleted requests.

        """
        request_id = request.tokens['REQ.REQUEST_ID'] if 'REQ.REQUEST_ID' in request.tokens else '0'
        delete_request(self.http_session, int(request_id))
        del request.tokens['REQ.REQUEST_ID']
        return request
