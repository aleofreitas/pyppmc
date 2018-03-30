# -*- coding: utf-8 -*-
# TODO Implement test cases for non admin users. Users mus login, but can't have access to administrative features.

import inspect
import sys
import unittest

from pyppmc.session import Session
from requests import ConnectionError
from tests import TestData


class LogonTestCase(unittest.TestCase, TestData):

    def test_invalid_url(self):
        """Test logging on using invalid URL."""
        base_url = 'http://invalid_url'
        username = self.admin_username
        password = self.admin_password
        language = self.language
        with self.assertRaises(ConnectionError, msg='Exception not raised when invalid URL was passed.'):
            Session(base_url, username, password, language)

    def test_invalid_username(self):
        """Test logging on using invalid username."""
        base_url = self.base_url
        username = self.admin_username[::-1]
        password = self.admin_password
        language = self.language
        with self.assertRaises(RuntimeError, msg='Exception not raised when invalid user was passed.'):
            Session(base_url, username, password, language)

    def test_invalid_password(self):
        """Test logging on using invalid password."""
        base_url = self.base_url
        username = self.admin_username
        password = self.admin_password[::-1]
        language = self.language
        with self.assertRaises(RuntimeError, msg='Exception not raised when invalid password was passed.'):
            Session(base_url, username, password, language)

    def test_invalid_language(self):
        """Test logging on using invalid language."""
        base_url = self.base_url
        username = self.admin_username
        password = self.admin_password
        language = 'WESTRON'
        with self.assertRaises(ValueError, msg='Exception not raised when invalid language was passed.'):
            Session(base_url, username, password, language)

    def test_valid_data(self):
        """Test logging on using valid data."""
        """Test logging on using invalid password"""
        base_url = self.base_url
        username = self.admin_username
        password = self.admin_password
        language = self.language
        session = Session(base_url, username, password, language)
        self.assertGreater(len(session.http_session.cookies), 0, 'Failed to log onto PPM.')


if __name__ == '__main__':
    suite = suite = unittest.TestSuite()
    for cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if issubclass(cls[1], unittest.TestCase):
            for method in dir(cls[1]):
                if method == 'runTest' or method.startswith('test_'):
                    suite.addTest(cls[1](method))
    unittest.TextTestRunner(verbosity=2).run(suite)
