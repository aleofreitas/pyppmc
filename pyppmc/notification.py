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

"""Module containing SMTP methods.

"""

import smtplib

from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# noinspection SpellCheckingInspection
def send(host, port, rcpt_from, rcpt_to, username='', password='', starttls=False, rcpt_cc='', rcpt_bcc='',
         subject='', message='', mime_type='plain'):
    """Sends an e-mail message.

    Parameters
    ----------
    host : str
        SMTP server.
    port : int
        SMTP server port.
    rcpt_from : str
        E-mail address of the message sender.
    rcpt_to : str
        Semicolon (;) separated list of e-mail addresses to be sent a notification via To field.
    username : str, optional
        Username to authenticate on SMTP server.
    password : str, optional
        Password of the username to authenticate on SMTP server. Required if username is informed.
    starttls : bool, optional
        Flag to indicate if the connection to the SMTP server must use STARTTLS or not. Default is False (do not use).
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

    Returns
    -------
    dict
        Refused recipients.

    """
    if mime_type not in ['plain', 'html']:
        raise ValueError("Invalid MIME type: %s. Valid values are: 'plain', 'html'.")
    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = rcpt_from
    msg['To'] = rcpt_to
    msg['Cc'] = rcpt_cc
    contents = MIMEText(message, mime_type, 'utf-8')
    msg.attach(contents)

    server = smtplib.SMTP(host, port)
    if starttls:
        server.starttls()
    if username != '' and password != '':
        server.login(username, password)
    server.set_debuglevel(False)

    try:
        rcpt = list(set(rcpt_to.split(';') + rcpt_cc.split(';') + rcpt_bcc.split(';')))
        return server.sendmail(rcpt_from, rcpt, msg.as_string())
    finally:
        server.quit()
