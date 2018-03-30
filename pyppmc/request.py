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

"""Module containing request classes and methods.

"""


class RequestType(object):
    """A Request Type definition.

    Parameters
    ----------
    id : int, optional
        ID of the request type.
    name : str, optional
        Name of the request type.
    description : str, optional
        Description of the request type.
    reference_code : str, optional
        Reference code of the request type.
    fields : dict of str : :[obj]:`Field`, optional
        Dictionary of request type field definitions.
    field_groups : list of int, optional
        List of field group IDs enabled on the request_type.

    Attributes
    ----------
    id : int
        ID of the request type.
    name : str
        Name of the request type.
    description : str
        Description of the request type.
    reference_code : str
        Reference code of the request type.
    fields : dict of str : :[obj]:`Field`
        Dictionary of request type field definitions.
    field_groups : list of int
        List of field group IDs enabled on the request_type.

    """

    @property
    def is_pfm_proposal(self):
        return 11 in (self.field_groups or [])

    @property
    def is_pfm_project(self):
        return 12 in (self.field_groups or [])

    @property
    def is_pfm_asset(self):
        return 13 in (self.field_groups or [])

    def __init__(self, persister=None, id=None, name=None, description=None, reference_code=None, fields=None,
                 field_groups=None):
        self.persister = persister
        self.id = id
        self.name = name
        self.description = description
        self.reference_code = reference_code
        self.fields = fields or dict()
        self.field_groups = field_groups or list()


class RequestField(object):
    """A request field definition.

    Parameters
    ----------
    persister : :[obj]:`Object`, optional
        Object used to persist field data.
    name : str, optional
        Field name.
    prompt : str, optional
        Field prompt.
    description : str, optional
        Field description.
    section : str, optional
        Field section name.
    validation_id : int, optional
        ID of the field validation_id.
    data_type : str, optional
        Type of field data.
    max_length : int, optional
        Field maximum legth.
    default_value str, optional
        Field devault value.
    required : bool, optional
        Flag that defines whether field is required or not.
    multi : bool, optional
        ***Flag that defines whether field is multi-select or not.
    display : bool, optional
        ***Flag that defines whether field is displayed or not.
    display_only : bool, optional
        ***Flag that defines whether field is editable or not.
    read_only : bool, optional
        ***Flag that defines whether field is read only or not.
    create_only : bool, optional
        ***Flag that defines whether field is for create only or not.
    update_only : bool, optional
        ***Flag that defines whether field is for update only or not.
    migrate_ok : bool, optional
        ***Flag that defines whether field is ok for migration or not.
    view_restricted : bool, optional
        ***Flag that defines whether field is restricted for view or not.
    edit_restricted : bool, optional
        ***Flag that defines whether field is for restricted for edit or not.

    Attributes
    ----------
    persister : :[obj]:`Object`
        Object used to persist field data.
    name : str
        Field name.
    prompt : str
        Field prompt.
    description : str
        Field description.
    section : str
        Field section name.
    validation_id : int
        ID of the field validation_id.
    data_type : str
        Type of field data.
    max_length : int
        Field maximum legth.
    default_value str
        Field devault value.
    required : bool
        Flag that defines whether field is required or not.
    multi : bool
        ***Flag that defines whether field is multi-select or not.
    display : bool
        ***Flag that defines whether field is displayed or not.
    display_only : bool
        ***Flag that defines whether field is editable or not.
    read_only : bool
        ***Flag that defines whether field is read only or not.
    create_only : bool
        ***Flag that defines whether field is for create only or not.
    update_only : bool
        ***Flag that defines whether field is for update only or not.
    migrate_ok : bool
        ***Flag that defines whether field is ok for migration or not.
    view_restricted : bool
        ***Flag that defines whether field is restricted for view or not.
    edit_restricted : bool
        ***Flag that defines whether field is for restricted for edit or not.

    """

    def __init__(self, persister=None, name=None, prompt=None, description=None, section=None, validation_id=None,
                 data_type=None, max_length=None, default_value=None, required=False, multi=False, display=False,
                 display_only=False, read_only=False, create_only=False, update_only=False, migrate_ok=False,
                 view_restricted=False, edit_restricted=False):
        self.persister = persister
        self.name = name
        self.prompt = prompt
        self.description = description
        self.section = section
        self.validation_id = validation_id
        self.data_type = data_type
        self.max_length = max_length
        self.default_value = default_value
        self.required = required
        self.multi = multi
        self.display = display
        self.display_only = display_only
        self.read_only = read_only
        self.create_only = create_only
        self.update_only = update_only
        self.migrate_ok = migrate_ok
        self.view_restricted = view_restricted
        self.edit_restricted = edit_restricted


# TODO Implement a collection for request notes.
class Request(object):
    """A Request object.

    Parameters
    ----------
    persister : :[obj]:, optional
        Object used to persist request data.
    id : int, optional
        ID of the request.
    description : str, optional
        Description of the request.
    request_type : str, optional
        Name of the request type.
    source_type : str, optional
        Name of the source type.
    source : str, optional
        Source identifier.
    fields : dict of str : :[obj]:`Object`, optional
        Request fields.

    Attributes
    ----------
    persister : :[obj]:`Object`
        Object used to persist request data.
    id : int
        ID of the request.
    description : str
        Description of the request.
    request_type : str
        Name of the request type.
    source_type : str
        Name of the source type.
    source : str
        Source identifier.
    fields : dict of str : :[obj]:`Object`
        Request fields.

    """

    @property
    def id(self):
        if 'REQ.REQUEST_ID' in self.fields:
            return self.fields['REQ.REQUEST_ID']

    @id.setter
    def id(self, value):
        self.fields['REQ.REQUEST_ID'] = value

    @property
    def description(self):
        if 'REQ.DESCRIPTION' in self.fields:
            return self.fields['REQ.DESCRIPTION']

    @description.setter
    def description(self, value):
        self.fields['REQ.DESCRIPTION'] = value

    @property
    def request_type(self):
        if 'REQ.REQUEST_TYPE_NAME' in self.fields:
            return self.fields['REQ.REQUEST_TYPE_NAME']

    @request_type.setter
    def request_type(self, value):
        self.fields['REQ.REQUEST_TYPE_NAME'] = value

    def __init__(self, persister=None, id=None, description=None, request_type=None, source_type=None, source=None,
                 fields=None):
        self.persister = persister
        self.source_type = source_type
        self.fields = fields or dict()
        self.id = id
        self.description = description
        self.request_type = request_type
        self.source = source

    def save(self):
        """Saves request data.

        """
        self.persister.save(self)

    def delete(self):
        """Deletes the request from PPM.

        """
        self.persister.delete(self)
