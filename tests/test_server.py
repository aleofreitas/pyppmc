# -*- coding: utf-8 -*-

import inspect
import security
import sys
import unittest

from pyppmc.session import Session
from pyppmc.server import Server
from tests import TestData


class LanguageTestCase(unittest.TestCase, TestData):

    def test_get_language(self):
        """Test getting languages from logon page."""
        langs = Server.get_languages(self.base_url)
        print 'Available languages: ', langs
        self.assertGreater(len(langs), 0, 'Failed to retrieve languages from login page.')


class LogonTestCase(unittest.TestCase, TestData):

    def setUp(self):
        session = Session(self.base_url, self.admin_username, self.admin_password, self.language)
        self.assertGreater(len(session.http_session.cookies), 0, 'Failed to log onto PPM.')
        server = Server(session)
        server.public_key = security.get_public_key(self.public_key_file)
        server.private_key = security.get_private_key(self.private_key_file)
        self.server = server


class SendNotificationTestCase(LogonTestCase):
    def test_invalid_mime_type(self):
        """Test sending notification with invalid MIME type."""
        with self.assertRaises(ValueError, msg='No exception raised when invalid MIME type was passed.'):
            self.server.send_notification(self.mail_to, rcpt_cc=self.mail_cc, rcpt_bcc=self.mail_bcc, subject='Test',
                                          message="No message", mime_type='INVALID_MIME')

    def test_plain_notification(self):
        """Test sending plain notification."""
        result = self.server.send_notification(self.mail_to, rcpt_cc=self.mail_cc, rcpt_bcc=self.mail_bcc,
                                               subject='Test', message="If you're Brazilian, then 'isto é um teste!', "
                                                                       "else 'this is a test!'")
        self.assertNotIsInstance(result, dict.__class__, 'Notification was not sent.')

    def test_html_notification(self):
        """Test sending HTML notification."""
        message = """\
        <HTML>
            <BODY>
                <p>
                    If you're <b style="color: red">Brazilian</b>, then 
                    <b style="color: blue">'isto é um teste!'</b><br/>
                    Else <b style="color: blue">'this is a test!'</b><br/>
                </p>
            <BODY>
        </HTML>
        """
        result = self.server.send_notification(self.mail_to, rcpt_cc=self.mail_cc, rcpt_bcc=self.mail_bcc,
                                               subject='Test', message=message, mime_type='html')
        self.assertNotIsInstance(result, dict.__class__, 'Notification was not sent.')


class SQLRunnerTestCase(LogonTestCase):
    def test_export_txt_query(self):
        """Test exporting SQL query to txt format."""
        result = self.server.export_query("SELECT request_id, description FROM kcrt_requests WHERE ROWNUM <= 5", 'txt')
        print '\n' + result
        self.assertGreater(len(result), 0, 'Failed to run query against db.')

    def test_export_csv_query(self):
        """Test exporting SQL query to csv format."""
        result = self.server.export_query("SELECT request_id, description FROM kcrt_requests WHERE ROWNUM <= 5", 'csv')
        print '\n' + result
        self.assertGreater(len(result), 0, 'Failed to run query against db.')

    def test_run_query(self):
        """Test running a SQL query."""
        result = self.server.run_query("SELECT request_id, description FROM kcrt_requests WHERE ROWNUM <= 5")
        for row in result:
            print row[0], row[1]
        self.assertGreater(len(result), 0, 'Failed to run query against db.')


if __name__ == '__main__':
    suite = suite = unittest.TestSuite()
    for cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if issubclass(cls[1], unittest.TestCase):
            for method in dir(cls[1]):
                if method == 'runTest' or method.startswith('test_'):
                    suite.addTest(cls[1](method))
    unittest.TextTestRunner(verbosity=2).run(suite)
