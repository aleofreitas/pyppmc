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

"""tm.py

Module containing Time Management RESTful web services operations.

Attributes
----------
PERIODS_PATH
    Path to Periods collection.
POLICIES_PATH
    Path to policies collection.
TIME_PERIODS_PATH
    Path to timePeriods collection.
TIME_SHEETS_PATH
    Path to timeSheets collection.
TIME_SHEET_LINES_PATH
    Path to timeSheetLines collection.
WORK_ITEMS_PATH
    Path to workItems collection.

"""

import rest

PERIODS_PATH = '/itg/rest/tm/Periods'
POLICIES_PATH = '/itg/rest/tm/policies'
TIME_PERIODS_PATH = '/itg/rest/tm/timePeriods'
TIME_SHEETS_PATH = '/itg/rest/tm/timeSheets'
TIME_SHEET_LINES_PATH = '/itg/rest/tm/timeSheetLines'
WORK_ITEMS_PATH = '/itg/rest/tm/workItems'


# TODO Rewrite method to return a list of time sheets.
def get_time_sheets(http_session, user_id, period_id):
    """Returns time sheets for the given user in the given period.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    user_id : int
        ID of the time sheet owner.
    period_id : int
        Time period id.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = TIME_SHEETS_PATH
    params = {
        'ownerUserId': user_id,
        'periodId': period_id
    }
    return rest.call_operation(http_session, 'GET', path, params=params, message_type='json')


# TODO Rewrite method to return a time sheet object.
def get_time_sheet(http_session, time_sheet_id):
    """Returns time sheet details for the given id.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    time_sheet_id : int
        ID of the time sheet.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = '%s/%d' % (TIME_SHEETS_PATH, time_sheet_id)
    return rest.call_operation(http_session, 'GET', path, message_type='json')


# TODO Rewrite method to return a list of time periods.
def get_time_periods(http_session, period_type_id, date):
    """Returns time periods of given type for given date.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    period_type_id : int
        ID of the period type.
    date : :[obj]:`datetime`
        Date to find time periods for.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = TIME_PERIODS_PATH
    params = {
        'type': period_type_id,
        'date': rest.datetime_to_iso(date)
    }
    return rest.call_operation(http_session, 'GET', path, params=params, message_type='json')


# TODO Rewrite method to return a time period object.
def get_time_period(http_session, period_id):
    """Returns time period details for given id.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    period_id : int
        ID of the time period.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = '%s/%d' % (TIME_PERIODS_PATH, period_id)
    return rest.call_operation(http_session, 'GET', path, message_type='json')


# TODO Rewrite method to return a list of work items.
def get_work_items(http_session, work_item_type, user_id):
    """Returns work items of given type for given user.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    work_item_type : str
        Work item type. Valid values are REQUEST, PACKAGE, TASK, PROJECT and MISC.
    user_id : int
        User id of the work item.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    Raises
    ------
    ValueError
        If an invalid work item type is passed to work_item_type.

    """
    path = WORK_ITEMS_PATH
    valid_types = ['REQUEST', 'PACKAGE', 'TASK', 'PROJECT', 'MISC']
    if work_item_type not in valid_types:
        raise ValueError('Invalid work item type: %s. Valid Values are %s' % (work_item_type, ', '.join(valid_types)))
    params = {
        'type': work_item_type,
        'ownerUserId': user_id

    }
    return rest.call_operation(http_session, 'GET', path, params=params, message_type='json')


# TODO Rewrite method to return a list of time sheet lines.
def get_time_sheet_lines(http_session, time_sheet_id):
    """Returns lines of given time sheet.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    time_sheet_id : int
        Time sheet id.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = '%s/%d/timeSheetLines' % (TIME_SHEETS_PATH, time_sheet_id)
    return rest.call_operation(http_session, 'GET', path, message_type='json')


# TODO Rewrite method to return a time sheet line object.
def get_time_sheet_line(http_session, time_sheet_line_id):
    """Returns details for given time sheet line.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    time_sheet_line_id : int
        Time sheet line id.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = '%s/%d' % (TIME_SHEET_LINES_PATH, time_sheet_line_id)
    return rest.call_operation(http_session, 'GET', path, message_type='json')


# TODO Rewrite method to return a list of time sheet policies.
def get_time_sheet_policies(http_session, user_id):
    """Returns time sheet policies for the given user.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    user_id : int
        Time sheet owner user id.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = POLICIES_PATH
    params = {
        'ownerUserId': user_id
    }
    return rest.call_operation(http_session, 'GET', path, params=params, message_type='json')


# TODO Rewrite method to return a time sheet object.
def create_time_sheet(http_session, payload):
    """Creates a new time sheet.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    payload : str
        Payload string.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = TIME_SHEETS_PATH
    return rest.call_operation(http_session, 'POST', path, data=payload, message_type='json')


# TODO Rewrite method to return a time sheet object.
def update_time_sheet(http_session, time_sheet_id, payload):
    """Updates the given time sheet.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    time_sheet_id : int
        Time sheet id.
    payload : str
        Payload string.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = '%s/%d' % (TIME_SHEETS_PATH, time_sheet_id)
    return rest.call_operation(http_session, 'PUT', path, data=payload, message_type='json')


# TODO Rewrite method to return a time sheet object.
def submit_time_sheet(http_session, time_sheet_id):
    """Submits the given time sheet.

    Parameters
    ----------
    http_session : :[obj]:`Session`
        HTTP session object.
    time_sheet_id : int
        Time sheet id.

    Returns
    -------
    :[obj]:`Response`
        HTTP Response object for the operation.

    """
    path = '%s/%d/actions/submit' % (TIME_SHEETS_PATH, time_sheet_id)
    return rest.call_operation(http_session, 'POST', path, message_type='json')
