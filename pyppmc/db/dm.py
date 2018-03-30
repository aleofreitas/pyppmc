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

"""Module containing Demand Management db methods.

"""

# TODO Implement method find, which will accept fields with values as a filter.
# TODO Review module constants.
# TODO Implement function to move requests in their workflows.
# TODO Function validate must check if request ID exists if operation is an update.

import cx_Oracle

from pyppmc.request import RequestType, RequestField, Request
from foundation import FieldPersister, ValidationPersister

"""
    1. Depending on the name, if PPM can't find the value it creates the request and returns no errors (e.g. 
       REQ.CONTACT_EMAIL).
    2. Editable fields (e.g. REQ.WORKFLOW_ID) can be found by querying KNTA_PARAMETER_SET_FIELDS table.
    3. Referenced fields (e.g. REQ.WORKFLOW_NAME) and the method to resolve them can be found by querying 
       KNTA_ENTITY_TOKENS_NLS table.
    4. Class must keep a list of default fields that it will return, which will be all referenced fields related to 
       editable fields plus REQ.LAST_UPDATE_DATE, REQ.ENTITY_LAST_UPDATE_DATE and REQ.STATUS_CODE.
"""

__ENTITY_TOKEN_LIST__ = ['REQ.APPLICATION_NAME', 'REQ.ASSIGNED_TO_GROUP_NAME', 'REQ.ASSIGNED_TO_NAME',
                         'REQ.CONTACT_EMAIL', 'REQ.CONTACT_NAME', 'REQ.CONTACT_PHONE_NUMBER', 'REQ.CREATED_BY',
                         'REQ.CREATION_DATE', 'REQ.DEPARTMENT_NAME', 'REQ.DESCRIPTION', 'REQ.ENTITY_LAST_UPDATE_DATE',
                         'REQ.LAST_UPDATE_DATE', 'REQ.PERCENT_COMPLETE', 'REQ.PRIORITY_NAME', 'REQ.REQUEST_GROUP_NAME',
                         'REQ.REQUEST_ID', 'REQ.REQUEST_SUB_TYPE_NAME', 'REQ.REQUEST_TYPE_NAME', 'REQ.STATUS_CODE',
                         'REQ.STATUS_NAME', 'REQ.WORKFLOW_NAME']
REQUEST_ENTITY_ID = 20
REQUEST_TYPE_ENTITY_ID = 19
REQUEST_HEADER_TYPE_ENTITY_ID = 39

# TODO Review allowed component types for request header types (SOAP, Rest).
# REQUEST_HEADER_ALLOWED_COMPONENT_TYPES = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 15, 19, 22]
IMMUTABLE_TOKENS = ['REQ.CREATED_BY_NAME', 'REQ.CREATED_BY_USERNAME', 'REQ.CREATED_BY_EMAIL',
                    'REQ.CREATION_DATE', 'REQ.CREATED_BY', 'REQ.LAST_UPDATED_BY_USERNAME',
                    'REQ.LAST_UPDATED_BY_EMAIL', 'REQ.LAST_UPDATE_DATE', 'REQ.LAST_UPDATED_BY',
                    'REQ.REQUEST_TYPE_NAME', 'REQ.REQUEST_TYPE_ID', 'REQ.REQUEST_ID', 'REQ.WORKFLOW_NAME',
                    'REQ.WORKFLOW_ID', 'REQ.STATUS_NAME', 'REQ.STATUS_ID', 'REQ.STATUS_CODE',
                    'REQ.CONTACT_PHONE_NUMBER', 'REQ.CONTACT_EMAIL', 'REQD.CREATION_DATE',
                    'REQD.LAST_UPDATE_DATE', 'REQD.WORKFLOW_ID', 'REQD.CREATED_BY', 'REQD.REQUEST_ID',
                    'REQD.LAST_UPDATED_BY', 'SYS.USERNAME', 'SYS.USER_ID']

NON_EXPANDABLE = ['REQ.APPLICATION_CODE', 'REQ.APPLICATION_NAME', 'REQ.ASSIGNED_TO_EMAIL', 'REQ.ASSIGNED_TO_GROUP_ID',
                  'REQ.ASSIGNED_TO_GROUP_NAME', 'REQ.ASSIGNED_TO_NAME', 'REQ.ASSIGNED_TO_USERNAME',
                  'REQ.ASSIGNED_TO_USER_ID', 'REQ.COMPANY', 'REQ.COMPANY_NAME', 'REQ.CONTACT_EMAIL', 'REQ.CONTACT_NAME',
                  'REQ.CONTACT_PHONE_NUMBER', 'REQ.CREATED_BY', 'REQ.CREATED_BY_EMAIL', 'REQ.CREATED_BY_NAME',
                  'REQ.CREATED_BY_USERNAME', 'REQ.CREATION_DATE', 'REQ.DEPARTMENT_CODE', 'REQ.DEPARTMENT_NAME',
                  'REQ.DESCRIPTION', 'REQ.LAST_UPDATED_BY', 'REQ.LAST_UPDATED_BY_EMAIL', 'REQ.LAST_UPDATED_BY_USERNAME',
                  'REQ.LAST_UPDATE_DATE', 'REQ.ENTITY_LAST_UPDATE_DATE', 'REQ.STATUS_CODE',
                  'REQ.MOST_RECENT_NOTE_AUTHORED_DATE', 'REQ.MOST_RECENT_NOTE_AUTHOR_FULL_NAME',
                  'REQ.MOST_RECENT_NOTE_AUTHOR_USERNAME', 'REQ.MOST_RECENT_NOTE_CONTEXT', 'REQ.MOST_RECENT_NOTE_TEXT',
                  'REQ.MOST_RECENT_NOTE_TYPE', 'REQ.MOST_RECENT_USER_NOTE_AUTHORED_DATE',
                  'REQ.MOST_RECENT_USER_NOTE_AUTHOR_FULL_NAME', 'REQ.MOST_RECENT_USER_NOTE_AUTHOR_USERNAME',
                  'REQ.MOST_RECENT_USER_NOTE_CONTEXT', 'REQ.MOST_RECENT_USER_NOTE_TEXT', 'REQ.NOTES',
                  'REQ.PERCENT_COMPLETE', 'REQ.PRIORITY_CODE', 'REQ.PRIORITY_NAME', 'REQ.PROJECT_CODE',
                  'REQ.PROJECT_NAME', 'REQ.REQUEST_GROUP_CODE', 'REQ.REQUEST_GROUP_NAME', 'REQ.REQUEST_ID',
                  'REQ.REQUEST_ID_LINK', 'REQ.REQUEST_SUB_TYPE_ID', 'REQ.REQUEST_SUB_TYPE_NAME', 'REQ.REQUEST_TYPE_ID',
                  'REQ.REQUEST_TYPE_NAME', 'REQ.REQUEST_URL', 'REQ.STATUS_ID', 'REQ.STATUS_NAME', 'REQ.SUBMIT_DATE',
                  'REQ.WORKBENCH_REQUEST_TYPE_URL', 'REQ.WORKBENCH_REQUEST_URL', 'REQ.WORKFLOW_ID', 'REQ.WORKFLOW_NAME',
                  'REQD.CREATED_BY', 'REQD.CREATION_DATE', 'REQD.LAST_UPDATED_BY', 'REQD.LAST_UPDATE_DATE',
                  'REQD.REQUEST_DETAIL_ID', 'REQD.REQUEST_ID', 'REQD.REQUEST_TYPE_ID']

ENTITY_FIELD_MAP = {'REQ.REQUEST_TYPE_ID': 'REQ.REQUEST_TYPE_NAME',
                    'REQ.WORKFLOW_ID': 'REQ.WORKFLOW_NAME',
                    'REQ.STATUS_ID': 'REQ.STATUS_NAME',
                    'REQ.PRIORITY_CODE': 'REQ.PRIORITY_NAME',
                    'REQ.APPLICATION_CODE': 'REQ.APPLICATION_NAME',
                    'REQ.DEPARTMENT_CODE': 'REQ.DEPARTMENT_NAME',
                    'REQ.REQUEST_SUB_TYPE_ID': 'REQ.REQUEST_SUB_TYPE_NAME',
                    'REQ.ASSIGNED_TO_USER_ID': 'REQ.ASSIGNED_TO_NAME',
                    'REQ.ASSIGNED_TO_GROUP_ID': 'REQ.ASSIGNED_TO_GROUP_NAME',
                    'REQ.REQUEST_GROUP_CODE': 'REQ.REQUEST_GROUP_NAME',
                    'REQ.COMPANY': 'REQ.COMPANY_NAME',
                    'REQ.CONTACT_NAME_ID': 'REQ.CONTACT_NAME'}

MIGRATE_FIELD_TOKENS = ['REQ.CREATED_BY', 'REQ.CREATION_DATE', 'REQ.WORKFLOW_STEP_ID']

STATUS_NOT_SUBMITTED = 14


def get_request_type(session, request_type_id):
    """Returns details about the given request type.

    Parameters
    ----------
    session : :[obj]:`Session`
        A valid PPM session.
    request_type_id : int
        ID of the request_type.

    Returns
    -------
    :[obj]:`RequestType`
        Object containing request type data.

    """
    rtp = RequestTypePersister(session)
    return rtp.get(request_type_id)


def get_request(session, request_id):
    """Returns details about the given request.

    Parameters
    ----------
    session : :[obj]:`Session`
        A valid PPM session.
    request_id : int
        ID of the request.

    Returns
    -------
    :[obj]:`Request`
        Object containing request data.

    """
    rp = RequestPersister(session)
    return rp.get(request_id)


def update_request(session, request):
    """Updates request data.

    Parameters
    ----------
    session : :[obj]:`Session`
        A valid PPM session.
    request : :[obj]:`Request`
        Request data to update.

    Returns
    -------
    :[obj]:`Request`
        Object containing updated request data.

    """
    rp = RequestPersister(session)
    return rp.save(request)


def delete_request(session, request):
    """Deletes a request.

    Parameters
    ----------
    session : :[obj]:`Session`
        A valid PPM session.
    request : :[obj]:`Request`

    Returns
    -------
    :[obj]:`Request`
        Request data without REQ.REQUEST_ID token set.

    """
    rp = RequestPersister(session)
    return rp.delete(request)


class RequestTypePersister(object):
    """Class to persist request type data on database.

    Parameters
    ----------
    session : :[obj]:`Session`, optional
        A valid PPM session.

    """

    def __init__(self, session=None):
        self.session = session

    # TODO Resulting Request object fields must have proper data types (e.g. a Date must be returned as a Date).
    def get(self, request_type_id):
        """Returns a request type definition.

        Parameters
        ----------
        request_type_id : int
            ID of the request type.

        Returns
        -------
        :[obj]:`RequestType`
            Object containing the give request type definition.

        """
        cur = self.session.db_con.cursor()
        request_type = RequestType(persister=self, id=request_type_id)

        cur.execute("""\
            SELECT request_type_name,
                   description,
                   reference_code
            FROM   kcrt_request_types_nls
            WHERE  request_type_id = :request_type_id""", request_type_id=request_type_id)
        request_header_type_id = None
        for row in cur:
            request_type.name = row[0]
            request_type.description = row[1]
            request_type.reference_code = row[2]

        contexts = self._get_contexts(request_type_id)
        fp = FieldPersister(self.session)
        fields = dict()

        # Retrieve header fields
        token_prefix = 'REQ'
        context_id = contexts['HEADER']
        for field in (fp.get_fields(context_id) or []):
            if field.table_name is None:
                field_name = '%s.%s' % (token_prefix, field.name)
                fields[field_name] = self.__get_request_field(field)
                if field_name in ENTITY_FIELD_MAP:
                    fields[ENTITY_FIELD_MAP[field_name]] = self.__get_request_field(field)
            else:
                field_name = '%s.P.%s' % (token_prefix, field.name)
                fields[field_name] = self.__get_request_field(field)

                field_name = '%s.VP.%s' % (token_prefix, field.name)
                fields[field_name] = self.__get_request_field(field)

        # Retrieve detail fields
        token_prefix = 'REQD'
        context_id = contexts['DETAIL']
        for field in (fp.get_fields(context_id) or []):
            field_name = '%s.P.%s' % (token_prefix, field.name)
            fields[field_name] = self.__get_request_field(field)

            field_name = '%s.VP.%s' % (token_prefix, field.name)
            fields[field_name] = self.__get_request_field(field)

        # Retrieve user data fields
        token_prefix = 'REQ'
        context_id = contexts['USER_DATA']
        for field in (fp.get_fields(context_id) or []):
            field_name = '%s.UD.%s' % (token_prefix, field.name)
            fields[field_name] = self.__get_request_field(field)

            field_name = '%s.VUD.%s' % (token_prefix, field.name)
            fields[field_name] = self.__get_request_field(field)

        # Set field groups
        field_groups = list()
        cur.execute("""\
            SELECT field_group_id
            FROM   kcrt_hdr_types_field_groups
            WHERE  request_header_type_id = :request_header_type_id""", request_header_type_id=request_header_type_id)
        for row in cur:
            field_groups += [row[0]]
        request_type.field_groups = list(field_groups)

        request_type.fields = dict(fields)
        return request_type

    def _get_contexts(self, request_type_id):
        """Returns a list of contexts related to the given request type.

        Parameters
        ----------
        request_type_id : int
            ID of the request type

        Returns
        -------
        dict of str : int
            Dictionary containing the context IDs related to the request type. Keys are HEADER, DETAIL and USER_DATA.

        """
        cur = self.session.db_con.cursor()
        cur.execute("""\
            SELECT request_header_type_id
            FROM   kcrt_request_types_nls
            WHERE  request_type_id = :request_type_id""", request_type_id=request_type_id)
        request_header_type_id = None
        for row in cur:
            request_header_type_id = row[0]

        context_query = """\
            SELECT parameter_set_context_id
            FROM   knta_parameter_set_contexts
            WHERE  entity_id = :entity_id
                   AND parameter_set_id = :parameter_set_id"""
        context_where = """
                   AND context_value = :context_value"""

        contexts = dict()

        # Header context
        entity_id = REQUEST_HEADER_TYPE_ENTITY_ID
        parameter_set_id = 217
        context_value = str(request_header_type_id)
        cur.prepare(context_query + context_where)
        cur.execute(None, entity_id=entity_id, parameter_set_id=parameter_set_id, context_value=context_value)
        for row in cur:
            contexts['HEADER'] = row[0]

        # Detail context
        entity_id = REQUEST_TYPE_ENTITY_ID
        parameter_set_id = 213
        context_value = str(request_type_id)
        cur.execute(None, entity_id=entity_id, parameter_set_id=parameter_set_id, context_value=context_value)
        for row in cur:
            contexts['DETAIL'] = row[0]

        # Request user data context
        entity_id = REQUEST_ENTITY_ID
        parameter_set_id = 208
        cur.execute(context_query, entity_id=entity_id, parameter_set_id=parameter_set_id)
        for row in cur:
            contexts['USER_DATA'] = row[0]

        return contexts

    def __get_request_field(self, field):
        """Returns a `RequestField` object from a `Field` object.

        Parameters
        ----------
        field : :[obj]:`Field`
            Field object to convert.

        Returns
        -------
        :[obj]:`RequestField`
            Resulting `RequestField` object.

        """
        cur = self.session.db_con.cursor()
        req_field = RequestField(persister=self, name=field.name, prompt=field.prompt, description=field.description,
                                 validation_id=field.validation_id, default_value=field.default_value[1],
                                 required=field.required, multi=field.multi, display=field.display,
                                 display_only=field.display_only)

        if field.section_id is None:
            req_field.read_only = False
            req_field.migrate_ok = False
        else:
            cur.execute("""\
                SELECT section_name
                FROM   knta_sections
                WHERE  section_id = :section_id""", section_id=field.section_id)
            for row in cur:
                req_field.section = row[0]

            if field.table_name is None:
                field_name = 'REQ.%s' % field.name
                req_field.migrate_ok = (field_name in MIGRATE_FIELD_TOKENS)
                req_field.read_only = (field_name in IMMUTABLE_TOKENS)

        vp = ValidationPersister(self.session)
        validation = vp.get(req_field.validation_id)
        req_field.max_length = validation.max_length
        req_field.data_type = self.__get_data_type(validation.component)

        return req_field

    def __get_data_type(self, component):
        """Returns the name of the field data type.

        Parameters
        ----------
        component : :[obj]:
            A component definition object.

        Returns
        -------
        str
            The name of the data type.

        """
        if component.component_type_code == 1:
            if component.data_mask_code == 'NUMERIC':
                return 'Numeric'
            elif component.data_mask_code == 'PERCENTAGE':
                return 'Percentage'
            elif component.data_mask_code == 'TELEPHONE':
                return 'Phone'
            else:
                return 'Text'
        elif component.component_type_code == 3:
            return 'Y/N'
        elif component.component_type_code == 7:
            return 'Date'
        elif component.component_type_code == 13:
            return 'Table'
        else:
            return 'Text'


class RequestPersister(object):
    """Class to persist request data on database.

    Parameters
    ----------
    session : :[obj]:`Session`, optional
        A valid PPM session.

    """

    def __init__(self, session=None):
        self.session = session

    def get(self, request_id):
        """Returns details of the given request.

        Parameters
        ----------
        request_id : int
            ID of the request.

        Returns
        -------
        :[obj]:`Request`
            Object containing details of the given request.

        Raises
        ------
        RuntimeError
            If a request with the given ID does not exist.

        """

        # TODO Verify if logged user has access to the request.
        # TODO Implement logic to parse tokens (some request fields have, like REQ.REQUEST_URL)
        cur = self.session.db_con.cursor()
        request = Request(persister=self)

        # Retrieve data from tables
        entity_data = dict()
        cur.execute("""\
            SELECT *
            FROM   kcrt_requests
            WHERE  request_id = :request_id""", request_id=request_id)
        for row in cur:
            for i, col in enumerate(row):
                entity_data[cur.description[i][0]] = col

        if cur.rowcount == 0:
            raise RuntimeError('Request %d does not exist.' % request_id)

        header_data = dict()
        batch_data = dict()
        cur.execute("""\
            SELECT *
            FROM   kcrt_req_header_details
            WHERE  request_id = :request_id""", request_id=request_id)
        for row in cur:
            for i, col in enumerate(row):
                batch_data[cur.description[i][0]] = col
            header_data[cur.rowcount] = dict(batch_data)

        detail_data = dict()
        batch_data = dict()
        cur.execute("""\
            SELECT *
            FROM   kcrt_request_details
            WHERE  request_id = :request_id""", request_id=request_id)
        for row in cur:
            for i, col in enumerate(row):
                batch_data[cur.description[i][0]] = col
            detail_data[cur.rowcount] = dict(batch_data)

        # Retrieve entity tokens information
        cur.execute("""\
            SELECT token,
                   column_name,
                   token_sql
            FROM   knta_entity_tokens_nls
            WHERE  entity_id = :entity_id""", entity_id=REQUEST_ENTITY_ID)
        entity_tokens = dict()
        for row in cur:
            entity_tokens[row[0]] = (row[1], row[2])

        request_type_id = entity_data['REQUEST_TYPE_ID']
        rtp = RequestTypePersister(self.session)
        request_type = rtp.get(request_type_id)
        contexts = rtp._get_contexts(request_type_id)

        fp = FieldPersister(self.session)

        # Retrieve header fields
        token_prefix = 'REQ'
        context_id = contexts['HEADER']
        for field in (fp.get_fields(context_id) or []):
            if field.table_name is None:
                field_name = '%s.%s' % (token_prefix, field.name)
                if entity_tokens[field.name][1] is None:
                    request.fields[field_name] = entity_data[entity_tokens[field.name][0]]
                else:
                    cur.prepare(entity_tokens[field.name][1])
                    params = dict()
                    for var in cur.bindnames():
                        params[var] = entity_data[var]
                    cur.execute(None, params)
                    value = None
                    for row in cur:
                        value = row[0]
                    request.fields[field_name] = value
            else:
                field_name = '%s.P.%s' % (token_prefix, field.name)
                request.fields[field_name] = header_data[field.batch_number]['PARAMETER%d' % field.column_number]

                field_name = '%s.VP.%s' % (token_prefix, field.name)
                request.fields[field_name] = header_data[field.batch_number][
                    'VISIBLE_PARAMETER%d' % field.column_number]

        # Retrieve detail fields
        token_prefix = 'REQD'
        context_id = contexts['DETAIL']
        for field in (fp.get_fields(context_id) or []):
            field_name = '%s.P.%s' % (token_prefix, field.name)
            request.fields[field_name] = detail_data[field.batch_number]['PARAMETER%d' % field.column_number]

            field_name = '%s.VP.%s' % (token_prefix, field.name)
            request.fields[field_name] = detail_data[field.batch_number]['VISIBLE_PARAMETER%d' % field.column_number]

        # Retrieve user data fields
        token_prefix = 'REQ'
        context_id = contexts['USER_DATA']
        for field in (fp.get_fields(context_id) or []):
            field_name = '%s.UD.%s' % (token_prefix, field.name)
            request.fields[field_name] = entity_data['USER_DATA%d' % field.column_number]

            field_name = '%s.VUD.%s' % (token_prefix, field.name)
            request.fields[field_name] = entity_data['VISIBLE_USER_DATA%d' % field.column_number]

        # Mask data
        # for field in request_type.fields:
        #     field_def = request_type.fields[field]
        #     if field_def.table_name == REQUEST_TABLE_NAME and 'USER_DATA' not in (field_def.column_name or '')\
        #             and field not in __ENTITY_TOKEN_LIST__:
        #         del request.fields[field]
        #     elif '.P.' in field or '.UD.' in field:
        #         del request.fields[field]

        # Additional ENTITY_LAST_UPDATE_DATE and STATUS_CODE tokens for Web Services compatibility
        request.fields['REQ.ENTITY_LAST_UPDATE_DATE'] = entity_data['ENTITY_LAST_UPDATE_DATE']
        request.fields['REQ.STATUS_CODE'] = entity_data['STATUS_CODE']

        return request

    def save(self, request):
        """Creates or updates the request.

        If REQ.REQUEST_ID name is present, the request is updated, otherwise it is created.

        Parameters
        ----------
        request : :[obj]:`Request`
            Object containing request data to persist.

        Returns
        -------
        :[obj]:`Request`
            The created or updated request object.

        Raises
        ------
        RuntimeError
            If create/update operation fails on database.

        """
        cur = self.session.db_con.cursor()

        # Delete additional ENTITY_LAST_UPDATE_DATE and STATUS_CODE tokens
        if 'REQ.ENTITY_LAST_UPDATE_DATE' in request.fields:
            del request.fields['REQ.ENTITY_LAST_UPDATE_DATE']
        if 'REQ.STATUS_CODE' in request.fields:
            del request.fields['REQ.STATUS_CODE']

        # Retrieve request type
        request_type_id = None
        if 'REQ.REQUEST_TYPE_ID' in request.fields:
            request_type_id = request.fields['REQ.REQUEST_TYPE_ID']
        elif request.request_type is not None:
            cur.execute("""\
                SELECT request_type_id
                FROM   kcrt_request_types 
                WHERE  request_type_name = :request_type_name""", request_type_name=request.request_type)
            for row in cur:
                request_type_id = row[0]
                break
        else:
            raise ValueError('Request data does not contain request type information.')
        rtp = RequestTypePersister(self.session)
        contexts = rtp._get_contexts(request_type_id)

        # Retrieve entity token information
        cur.execute("""\
            SELECT token,
                   column_name,
                   token_sql
            FROM   knta_entity_tokens_nls
            WHERE  entity_id = :entity_id""", entity_id=REQUEST_ENTITY_ID)
        entity_tokens = dict()
        for row in cur:
            entity_tokens[row[0]] = (row[1], row[2])

        # Set procedure output parameters
        last_update_date = cur.var(cx_Oracle.DATETIME)
        entity_last_update_date = cur.var(cx_Oracle.DATETIME)
        message_type = cur.var(cx_Oracle.NUMBER)
        message_name = cur.var(cx_Oracle.STRING)
        message = cur.var(cx_Oracle.STRING)

        # Check request ID
        event = 'INSERT'
        updated_flag = 'N'
        released_flag = 'N'
        status_id = STATUS_NOT_SUBMITTED
        if request.id is not None:
            event = 'UPDATE'

        # Initialize KCRT_REQUESTS_TH.PROCESS_ROW parameters
        params = dict()
        params['p_event'] = event
        params['p_request_id'] = None
        # TODO Change to logged user_id.
        params['p_last_updated_by'] = 1
        params['p_request_type_id'] = request_type_id
        params['p_request_subtype_id'] = None
        params['p_description'] = None
        params['p_release_date'] = None
        params['p_status_id'] = status_id
        params['p_workflow_id'] = None
        params['p_department_code'] = None
        params['p_priority_code'] = None
        params['p_application'] = None
        params['p_assigned_to_user_id'] = None
        params['p_assigned_to_group_id'] = None
        params['p_project_code'] = None
        params['p_contact_id'] = None
        params['p_updated_flag'] = updated_flag
        params['p_released_flag'] = released_flag
        params['p_company'] = None
        params['p_percent_complete'] = None
        params['p_source'] = request.source
        params['p_source_type_code'] = request.source_type
        params['p_user_data_set_context_id'] = None
        for i in range(1, 21):
            params['p_user_data%d' % i] = None
            params['p_visible_user_data%d' % i] = None
        params['p_usr_dbg'] = None
        params['o_last_update_date'] = last_update_date
        params['o_entity_last_update_date'] = entity_last_update_date
        params['o_message_type'] = message_type
        params['o_message_name'] = message_name
        params['o_message'] = message

        fp = FieldPersister(self.session)
        token_prefix = 'REQ'
        header_fields = fp.get_fields(contexts['HEADER'])
        for field in header_fields:
            field_name = '%s.%s' % (token_prefix, field.name)
            if field.table_name is None:
                if entity_tokens[field.name][1] is None \
                        and field_name not in MIGRATE_FIELD_TOKENS and field_name in request.fields:
                    params['p_' + entity_tokens[field.name][0].lower()] = request.fields[field_name]

        for field in fp.get_fields(contexts['USER_DATA']):
            field_name = '%s.UD.%s' % (token_prefix, field.name)
            if field_name in request.fields:
                params['p_user_data%d' % field.column_number] = request.fields[field_name]

            field_name = '%s.VUD.%s' % (token_prefix, field.name)
            if field_name in request.fields:
                params['p_visible_user_data%d' % field.column_number] = request.fields[field_name]

        request_id = cur.var(cx_Oracle.NUMBER)
        if event == 'UPDATE':
            request_id.setvalue(0, request.id)
        params['p_request_id'] = request_id
        cur.callproc('KCRT_REQUESTS_TH.PROCESS_ROW', keywordParameters=params)
        if message_type.getvalue() != 0:
            self.session.db_con.rollback()
            raise RuntimeError(message.getvalue())

        # Initialize KCRT_REQ_HEADER_DETAILS_TH.PROCESS_ROW parameters
        params = dict()
        params['p_event'] = event
        params['p_req_header_detail_id'] = None
        # TODO Change to logged user_id.
        params['p_last_updated_by'] = 1
        params['p_request_id'] = request_id.getvalue()
        params['p_request_type_id'] = request_type_id
        params['p_batch_number'] = None
        for i in range(1, 51):
            params['p_parameter%d' % i] = None
            params['p_visible_parameter%d' % i] = None
        params['p_usr_dbg'] = None
        params['o_last_update_date'] = last_update_date
        params['o_message_type'] = message_type
        params['o_message_name'] = message_name
        params['o_message'] = message

        batches = dict()
        token_prefix = 'REQ'
        for field in header_fields:
            if field.table_name is not None:
                if field.batch_number not in batches:
                    batches[field.batch_number] = dict(params)
                    batches[field.batch_number]['p_batch_number'] = field.batch_number

                field_name = '%s.P.%s' % (token_prefix, field.name)
                if field_name in request.fields:
                    batches[field.batch_number]['p_parameter%d' % field.column_number] = request.fields[field_name]

                field_name = '%s.VP.%s' % (token_prefix, field.name)
                if field_name in request.fields:
                    batches[field.batch_number]['p_visible_parameter%d' % field.column_number] = request.fields[
                        field_name]

        for i in batches:
            req_header_detail_id = cur.var(cx_Oracle.NUMBER)
            if event == 'UPDATE':
                cur.execute("""\
                    SELECT req_header_detail_id
                    FROM   kcrt_req_header_details
                    WHERE  request_id = :request_id
                           AND batch_number = :batch_number""", request_id=request_id.getvalue(),
                            batch_number=i)
                row = cur.fetchone()
                req_header_detail_id.setvalue(0, row[0])
            batches[i]['p_req_header_detail_id'] = req_header_detail_id
            cur.callproc('KCRT_REQ_HEADER_DETAILS_TH.PROCESS_ROW', keywordParameters=batches[i])
            if message_type.getvalue() != 0:
                self.session.db_con.rollback()
                raise RuntimeError(message.getvalue())

        # Initialize KCRT_REQUEST_DETAILS_TH.PROCESS_ROW parameters
        params = dict()
        params['p_event'] = event
        params['p_request_detail_id'] = None
        # TODO Change to logged user_id.
        params['p_last_updated_by'] = 1
        params['p_request_id'] = request_id.getvalue()
        params['p_request_type_id'] = request_type_id
        params['p_batch_number'] = None
        params['p_parameter_set_context_id'] = None
        for i in range(1, 51):
            params['p_parameter%d' % i] = None
            params['p_visible_parameter%d' % i] = None
        params['p_usr_dbg'] = None
        params['o_last_update_date'] = last_update_date
        params['o_message_type'] = message_type
        params['o_message_name'] = message_name
        params['o_message'] = message

        batches = dict()
        token_prefix = 'REQD'
        for field in fp.get_fields(contexts['DETAIL']):
            if field.batch_number not in batches:
                batches[field.batch_number] = dict(params)
                batches[field.batch_number]['p_batch_number'] = field.batch_number

            field_name = '%s.P.%s' % (token_prefix, field.name)
            if field_name in request.fields:
                batches[field.batch_number]['p_parameter%d' % field.column_number] = request.fields[field_name]

            field_name = '%s.VP.%s' % (token_prefix, field.name)
            if field_name in request.fields:
                batches[field.batch_number]['p_visible_parameter%d' % field.column_number] = request.fields[field_name]

        for i in batches:
            request_detail_id = cur.var(cx_Oracle.NUMBER)
            if event == 'UPDATE':
                cur.execute("""\
                    SELECT request_detail_id
                    FROM   kcrt_request_details
                    WHERE  request_id = :request_id
                           AND batch_number = :batch_number""", request_id=request_id.getvalue(),
                            batch_number=i)
                row = cur.fetchone()
                request_detail_id.setvalue(0, row[0])
            batches[i]['p_request_detail_id'] = request_detail_id
            cur.callproc('KCRT_REQUEST_DETAILS_TH.PROCESS_ROW', keywordParameters=batches[i])
            if message_type.getvalue() != 0:
                self.session.db_con.rollback()
                raise RuntimeError(message.getvalue())

        if event == 'INSERT':
            # Submit request
            params = dict()
            params['p_request_id'] = request_id.getvalue()
            # TODO Change to logged user_id.
            params['p_user_id'] = 1
            params['p_from_workflow_step_seq'] = None
            params['p_event'] = 'INSTANCE_SET_CREATE'
            params['p_result_visible_value'] = None
            params['p_schedule_date'] = None
            params['p_delegate_to_username'] = None
            params['p_to_workflow_step_seq'] = None
            params['p_run_interface'] = 'Y'

            cur.callproc("KCRT_REQUEST_UTIL.MOVE_REQUEST_WORKFLOW", keywordParameters=params)

        self.session.db_con.commit()

        req = self.get(request_id.getvalue())
        request.__dict__ = req.__dict__.copy()

        return request

    def delete(self, request):
        """Deletes the given request.

        Parameters
        ----------
        request : :[obj]:`Request`
            Object containing request data to delete.

        Returns
        -------
        :[obj]:`Request`
            Object containing deleted request data with REQ.REQUEST_ID name cleared.

        Raises
        ------
        RuntimeError
            If delete operation fails on database.

        """
        cur = self.session.db_con.cursor()

        request_id = cur.var(cx_Oracle.NUMBER)
        last_update_date = cur.var(cx_Oracle.DATETIME)
        entity_last_update_date = cur.var(cx_Oracle.DATETIME)
        message_type = cur.var(cx_Oracle.NUMBER)
        message_name = cur.var(cx_Oracle.STRING)
        message = cur.var(cx_Oracle.STRING)

        request_id.setvalue(0, request.id)
        params = dict()
        params['p_event'] = 'DELETE'
        params['p_request_id'] = request_id
        # TODO Change to logged user_id.
        params['p_last_updated_by'] = 1
        params['o_last_update_date'] = last_update_date
        params['o_entity_last_update_date'] = entity_last_update_date
        params['o_message_type'] = message_type
        params['o_message_name'] = message_name
        params['o_message'] = message

        cur.callproc('KCRT_REQUESTS_TH.PROCESS_ROW', keywordParameters=params)
        if message_type.getvalue() != 0:
            self.session.db_con.rollback()
            raise RuntimeError(message.getvalue())
        request.id = None

        self.session.db_con.commit()

        return request
