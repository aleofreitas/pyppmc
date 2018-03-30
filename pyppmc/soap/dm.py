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

Module containing Demand Management SOAP web services operations.

Attributes
----------
SERVICE_ENDPOINT : str
    Service endpoint path.

"""

import datetime
import lxml
import soap

from request import Request

SERVICE_ENDPOINT = '/itg/ppmservices/DemandService'


def get_requests(http_session, request_ids):
    """Returns details of the given requests.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    request_ids : list of int
        List of request ID to search.

    Returns
    -------
    list of :[obj]:`Request`
        List of request objects containing their data.

    """
    request_xml = """\
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
           xmlns:ns="http://mercury.com/ppm/dm/service/1.0" xmlns:ns1="http://mercury.com/ppm/dm/1.0">
           <soapenv:Header/>
           <soapenv:Body>
              <ns:getRequests>"""

    for id in request_ids:
        request_xml += """
                 <ns:requestIds>
                    <ns1:id>%d</ns1:id>
                 </ns:requestIds>""" % id

    request_xml += """
              </ns:getRequests>
           </soapenv:Body>
        </soapenv:Envelope>"""

    response = soap.call_operation(http_session, SERVICE_ENDPOINT, data=request_xml)
    ns = {
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
        'pre': 'http://mercury.com/ppm/dm/1.0',
        'common': 'http://mercury.com/ppm/common/1.0',
        'service': 'http://mercury.com/ppm/dm/service/1.0',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    requests = []
    tree = lxml.etree.fromstring(response.content)
    for ret in tree.xpath('//service:return', namespaces=ns):
        request = Request()
        request_type = ret.xpath('./pre:requestType/text()', namespaces=ns)[0]
        request.fields['REQ.REQUEST_TYPE_NAME'] = request_type
        for simpleFields in ret.xpath('./pre:simpleFields', namespaces=ns):
            token = simpleFields.xpath('./common:name/text()', namespaces=ns)[0]
            node = simpleFields.xpath('./pre:stringValue/text()', namespaces=ns)
            value = None
            if len(node) > 0:
                value = node[0]
            else:
                node = simpleFields.xpath('./pre:dateValue/text()', namespaces=ns)
                if len(node) > 0:
                    value = soap.iso_to_datetime(node[0])
            request.fields[token] = value
        requests += [request]
    return requests


def create_request(http_session, request):
    """Creates a new request.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    request : :[obj]:`Request`
        Request object containing its data.

    Returns
    -------
    int
        ID of the new request.

    """
    request_type = request.tokens['REQ.REQUEST_TYPE_NAME'] if 'REQ.REQUEST_TYPE_NAME' in request.tokens else ''

    request_xml = """\
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:ns="http://mercury.com/ppm/dm/service/1.0" xmlns:ns1="http://mercury.com/ppm/dm/1.0"
               xmlns:ns2="http://mercury.com/ppm/common/1.0">
               <soapenv:Header/>
               <soapenv:Body>
                  <ns:createRequest>
                     <ns:requestObj>"""

    if request_type != '':
        request_xml += '<ns1:requestType>%s</ns1:requestType>' % request_type

    # TODO Implement logic for tables, notes, fieldChangeNotes, URLReferences and remoteReferences.
    simple_fields = ''
    for token in request.tokens.keys():
        value = request.tokens[token]
        if isinstance(value, datetime.datetime):
            simple_fields += """
                        <ns1:simpleFields>
                           <ns2:name>%s</ns2:name>
                           <ns1:dateValue>%s</ns1:dateValue>
                        </ns1:simpleFields>""" % (token, soap.datetime_to_iso(value))
        else:
            simple_fields += """
                        <ns1:simpleFields>
                           <ns2:name>%s</ns2:name>
                           <ns1:stringValue>%s</ns1:stringValue>
                        </ns1:simpleFields>""" % (token, value)

    request_xml += simple_fields
    request_xml += """
                     </ns:requestObj>
                  </ns:createRequest>
               </soapenv:Body>
            </soapenv:Envelope>"""

    response = soap.call_operation(http_session, SERVICE_ENDPOINT, data=request_xml)
    ns = {
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
        'pre': 'http://mercury.com/ppm/dm/1.0',
        'common': 'http://mercury.com/ppm/common/1.0',
        'service': 'http://mercury.com/ppm/dm/service/1.0',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    tree = lxml.etree.fromstring(response.content)
    request_id = tree.xpath('//service:return/pre:identifier/pre:id/text()', namespaces=ns)[0]
    return int(request_id)


def set_request_fields(http_session, request_id, tokens):
    """Updates given fields in the given request.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    request_id : int
        Id of the request to update.
    tokens : dict of str : str
        Data to update.

    Returns
    -------
    int
        ID of the updated request.

    """
    request_xml = """\
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://mercury.com/ppm/dm/service/1.0" xmlns:ns1="http://mercury.com/ppm/dm/1.0" xmlns:ns2="http://mercury.com/ppm/common/1.0">
           <soap:Header/>
           <soap:Body>
              <ns:setRequestFields>
                 <ns:requestId>
                    <ns1:id>40092</ns1:id>
                 </ns:requestId>""" % request_id

    for token in tokens.keys():
        value = tokens[token]
        if isinstance(value, datetime.datetime):
            request_xml += """
                     <ns:fields>
                        <ns2:name>%s</ns2:name>
                        <ns1:dateValue>No</ns1:stringValue>
                     </ns:fields>""" % (token, soap.datetime_to_iso(value))
        else:
            request_xml += """
                     <ns:fields>
                        <ns2:name>%s</ns2:name>
                        <ns1:stringValue>%s</ns1:stringValue>
                     </ns:fields>""" % (token, value)

        request_xml += """
              </ns:setRequestFields>
           </soap:Body>
        </soap:Envelope>"""

    response = soap.call_operation(http_session, SERVICE_ENDPOINT, data=request_xml)
    ns = {
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
        'pre': 'http://mercury.com/ppm/dm/1.0',
        'common': 'http://mercury.com/ppm/common/1.0',
        'service': 'http://mercury.com/ppm/dm/service/1.0',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    tree = lxml.etree.fromstring(response.content)
    request_id = tree.xpath('//service:return/text()', namespaces=ns)[0]
    return int(request_id)


def delete_requests(http_session, request_ids):
    """Deletes the given requests.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    request_ids : list of int
        List of Request ID to delete.

    Returns
    -------
    int
        Number of requests deleted.

    """
    request_xml = """\
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://mercury.com/ppm/dm/service/1.0" xmlns:ns1="http://mercury.com/ppm/dm/1.0">
           <soapenv:Header/>
           <soapenv:Body>
              <ns:deleteRequests>"""

    for id in request_ids:
        request_xml += """
                 <ns:requestIds>
                    <ns1:id>%d</ns1:id>
                 </ns:requestIds>""" % id

    request_xml += """
              </ns:deleteRequests>
           </soapenv:Body>
        </soapenv:Envelope>"""

    response = soap.call_operation(http_session, SERVICE_ENDPOINT, data=request_xml)
    ns = {
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
        'pre': 'http://mercury.com/ppm/dm/1.0',
        'common': 'http://mercury.com/ppm/common/1.0',
        'service': 'http://mercury.com/ppm/dm/service/1.0',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    tree = lxml.etree.fromstring(response.content)
    count = tree.xpath('//service:return/text()', namespaces=ns)[0]
    return int(count)


class RequestSoap:
    """Request persistence class based on PPM SOAP Web Services.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        A request.Session session object.

    """

    def __init__(self, http_session):
        self.http_session = http_session

    def save(self, request):
        """Saves the request.

        If REQ.REQUEST_ID name is present on request object, then the given request is updated.
        Otherwise a new request is created.

        Parameters
        ----------
        request : :[obj]:`Request`
            Request object containing data to persist.

        Returns
        -------
        :[obj]:`Request`
            The new or updated request.

        """
        request_id = request.tokens['REQ.REQUEST_ID'] if 'REQ.REQUEST_ID' in request.tokens else '0'

        if int(request_id) > 0:
            # TODO Implement logic to update other objects using available operations (addRequestNotes, setRequestRemoteReferenceStatus)
            request_id = set_request_fields(self.http_session, int(request_id), request.tokens)
        else:
            request_id = create_request(self.http_session, request)

        req = get_requests(self.http_session, [request_id])[0]
        request.tokens = dict()
        for token in req.tokens.keys():
            request.tokens[token] = req.tokens[token]
        return request

    def get(self, request_id):
        """Returns details of the given request.

        Parameters
        ----------
        request_id : int
            Id of the request.

        Returns
        -------
        :[obj]:`Request`
            Request object containing its details.

        """
        request = get_requests(self.http_session, [request_id])[0]
        request.persister = self
        return request

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

        """
        request_id = request.tokens['REQ.REQUEST_ID'] if 'REQ.REQUEST_ID' in request.tokens else '0'
        if int(request_id) > 0:
            count = delete_requests(self.http_session, [int(request_id)])
            if count == 0:
                raise RuntimeError('Failed to delete request.')
            else:
                del request.tokens['REQ.REQUEST_ID']
        return request
