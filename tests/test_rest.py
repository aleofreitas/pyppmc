# -*- coding: utf-8 -*-

import datetime
import inspect
import sys
import unittest

from pyppmc.session import Session
from pyppmc.request import Request
from pyppmc.rest import dm
from tests import TestData

class DMTestCase(unittest.TestCase, TestData):

    def setUp(self):
        self.session = Session(self.base_url, self.admin_username, self.admin_password, self.language)
        self.assertGreater(len(self.session.http_session.cookies), 0, 'Failed to log onto PPM.')

    def test_create_get_and_delete_request(self):
        """Create, retrieve and delete a request."""
        # Create request
        persister = dm.RequestRest(self.session.http_session)
        request = Request(persister)
        request.fields['REQ.REQUEST_TYPE_NAME'] = 'Bug'
        request.fields['REQ.DEPARTMENT_CODE'] = 'Finance'
        request.fields['REQ.WORKFLOW_NAME'] = 'Bug Request Type Workflow'
        request.fields['REQ.DESCRIPTION'] = 'Test Create Request %s' % datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')
        request.fields['REQD.MODULE'] = 'Module A'
        request.fields['REQD.PLATFORM'] = 'Linux'
        # Accepts fields in full syntax
        request.fields['REQD.VP.IMPACT'] = 'Warning'
        # Accepts hidden fields
        request.fields['REQD.P.REPRO'] = 'Y'
        request.save()
        request_id = ''
        if 'REQ.REQUEST_ID' in request.fields:
            request_id = request.fields['REQ.REQUEST_ID']
            print 'Request ID: %s' % request_id
        self.assertIn('REQ.REQUEST_ID', request.fields, 'Failed to create request.')

        # Retrieve request
        request2 = persister.get(int(request_id))
        self.assertIsInstance(request2, Request, 'Failed to retrieve created request.')
        print 'Request %d fields:'
        for token in request2.tokens.keys():
            print '\t%s: %s' % (token, request2.tokens[token])
            self.assertEquals(request.fields[token], request2.tokens[token], 'Requests contain different data.')

        # Delete request
        request.delete()
        self.assertNotIn('REQ.REQUEST_ID', request.fields, 'Failed to delete request.')
        print 'Request %d successfully deleted.' % int(request_id)

    # TODO Implement test cases for Demand Management GET operations
    # TODO Implement test cases for Time Management operations


if __name__ == '__main__':
    suite = suite = unittest.TestSuite()
    for cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if issubclass(cls[1], unittest.TestCase):
            for method in dir(cls[1]):
                if method == 'runTest' or method.startswith('test_'):
                    suite.addTest(cls[1](method))
    unittest.TextTestRunner(verbosity=2).run(suite)
