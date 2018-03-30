# -*- coding: utf-8 -*-

import os


class TestData(object):

    @property
    def base_url(self):
        return os.environ['PYPPM_BASE_URL']

    @property
    def http_base_url(self):
        return os.environ['PYPPM_HTTP_BASE_URL']

    @property
    def https_base_url(self):
        return os.environ['PYPPM_HTTPS_BASE_URL']

    @property
    def admin_username(self):
        return os.environ['PYPPM_ADMIN_USERNAME']

    @property
    def admin_password(self):
        return os.environ['PYPPM_ADMIN_PASSWORD']

    @property
    def language(self):
        return os.environ['PYPPM_LANGUAGE']

    @property
    def public_key_file(self):
        return os.environ['PYPPM_PUBLIC_KEY_FILE']

    @property
    def private_key_file(self):
        return os.environ['PYPPM_PRIVATE_KEY_FILE']

    @property
    def private_key_file(self):
        return os.environ['PYPPM_PRIVATE_KEY_FILE']

    @property
    def db_dsn(self):
        return os.environ['PYPPM_DB_DSN']

    @property
    def db_username(self):
        return os.environ['PYPPM_DB_USERNAME']

    @property
    def db_password(self):
        return os.environ['PYPPM_DB_PASSWORD']

    @property
    def mail_to(self):
        return os.environ['PYPPM_MAIL_TO']

    @property
    def mail_cc(self):
        return os.environ['PYPPM_MAIL_CC']

    @property
    def mail_bcc(self):
        return os.environ['PYPPM_MAIL_BCC']
