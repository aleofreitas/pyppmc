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

"""Module containing foundation classes and methods.

"""


class Field():
    """Field definition data.

    Attributes
    ----------
    persister : :[obj]:`FieldPersister`
        Object to persist field data.
    id : int
        The ID of the field.
    name : str
        Field token.
    context_id : int
        Context ID that contains the field.
    prompt : str
        Field prompt.
    description : str
        Field description.
    column_number : int
        Index of the column.
    table_name : str
        Database table that contains the field data.
    validation_id : int
        ID of the field validation.
    default_type: int
        Type of the default value.
    default_value : tuple of (str, str)
        Field default value (hidden, visible).
    section_id : int
        ID of the section where the field resides.
    display : bool
        Indicates if the field is visible.
    display_only : bool
        Indicates if the field is visible, but not editable.
    updatable: bool
        Indicates if the field is updatable.
    required : bool
        Indicates if the field is required.
    enabled : bool
        Indicates if the field is enabled.
    multi : bool
        Indicates if multi selection is enabled on the field.
    batch_number : int
        Number of the batch that contains the field.
    visible_to_all : bool
        Indicates if the field is visible to all users.
    editable_by_all : bool
        Indicates if the field is editable by all users.
    reference_code : str
        Field reference code.

    Parameters
    ----------
    persister : :[obj]:`FieldPersister`, optional
        Object to persist field data.
    id : int, optional
        The ID of the field.
    name : str, optional
        Field token.
    context_id : int, optional
        Context ID that contains the field.
    prompt : str, optional
        Field prompt.
    description : str, optional
        Field description.
    column_number : int, optional
        Index of the column.
    table_name : str, optional
        Database table that contains the field data.
    validation_id : int, optional
        ID of the field validation.
    default_type: int, optional
        Type of the default value.
    default_value : tuple of (str, str), optional
        Field default value (hidden, visible).
    section_id : int, optional
        ID of the section where the field resides.
    display : bool, optional
        Indicates if the field is visible.
    display_only : bool, optional
        Indicates if the field is visible, but not editable.
    updatable: bool, optional
        Indicates if the field is updatable.
    required : bool, optional
        Indicates if the field is required.
    enabled : bool, optional
        Indicates if the field is enabled.
    multi : bool, optional
        Indicates if multi selection is enabled on the field.
    batch_number : int, optional
        Number of the batch that contains the field.
    visible_to_all : bool, optional
        Indicates if the field is visible to all users.
    editable_by_all : bool, optional
        Indicates if the field is editable by all users.
    reference_code : str, optional
        Field reference code.

    """

    def __init__(self, persister=None, id=None, name=None, context_id=None, prompt=None, description=None,
                 column_number=None, table_name=None, validation_id=None, default_type=None, default_value=(None, None),
                 section_id=None, display=None, display_only=None, updatable=None, required=None, enabled=None,
                 multi=None, batch_number=None, visible_to_all=None, editable_by_all=None, reference_code=None):
        self.persister = persister
        self.id = id
        self.name = name
        self.context_id = context_id
        self.prompt = prompt
        self.description = description
        self.column_number = column_number
        self.table_name = table_name
        self.validation_id = validation_id
        self.default_type = default_type
        self.default_value = default_value
        self.section_id = section_id
        self.display = display
        self.display_only = display_only
        self.updatable = updatable
        self.required = required
        self.enabled = enabled
        self.multi = multi
        self.batch_number = batch_number
        self.visible_to_all = visible_to_all
        self.editable_by_all = editable_by_all
        self.reference_code = reference_code


class Validation(object):

    def __init__(self, persister=None, id=None, name=None, description=None, component=None, max_length=None,
                 enabled=None, reference_code=None):
        self.persister = persister
        self.id = id
        self.name = name
        self.description = description
        self.component = component
        self.max_length = max_length
        self.enabled = enabled
        self.reference_code = reference_code

    class GenericComponent(object):

        def __init__(self):
            self.component_type_code = None
            self.validation_type_code = None
            self.data_mask_code = None

        def validate(self, value):
            return value, value

    class TextComponent(GenericComponent):

        def __init__(self, data_mask_code, max_length):
            super(Validation.TextComponent, self).__init__()
            self.component_type_code = 1
            self.data_mask_code = data_mask_code
            self.max_length = max_length

        def validate(self, value):
            value = str(value)
            if len(value) > self.max_length:
                raise ValueError('Value exceeds max field size of %d characters.' % self.max_length)

            if self.data_mask_code == 'ALPHA':
                return value, value
            elif self.data_mask_code == 'ALPHA_UPPER':
                return value.upper(), value.upper()
            elif self.data_mask_code == 'CURRENCY':
                # TODO Implement logic to parse and return a float.
                return value, value
            elif self.data_mask_code == 'CUSTOM':
                # TODO Implement logic to parse custom strings.
                return value, value
            elif self.data_mask_code == 'NUMERIC':
                # TODO Implement logic to parse numbers.
                return value, value
            elif self.data_mask_code == 'PERCENTAGE':
                # TODO Implement logic to parse percentage numbers.
                return value, value
            elif self.data_mask_code == 'TELEPHONE':
                # TODO Implement logic to parse telephone numbers.
                return value, value

    class DropDownListComponent(GenericComponent):

        def __init__(self):
            super(Validation.DropDownListComponent, self).__init__()
            self.component_type_code = 2

        def validate(self, value):
            return value, value

    class RadioButtonComponent(GenericComponent):

        def __init__(self):
            super(Validation.RadioButtonComponent, self).__init__()
            self.component_type_code = 3

        def validate(self, value):
            return value, value

    class AutoCompleteListComponent(GenericComponent):

        def __init__(self):
            super(Validation.AutoCompleteListComponent, self).__init__()
            self.component_type_code = 4

        def validate(self, value):
            return value, value

    class TextAreaComponent(GenericComponent):

        def __init__(self):
            super(Validation.TextAreaComponent, self).__init__()
            self.component_type_code = 5

        def validate(self, value):
            return value, value

    class DateComponent(GenericComponent):

        def __init__(self):
            super(Validation.DateComponent, self).__init__()
            self.component_type_code = 7

        def validate(self, value):
            return value, value

    class URLComponent(GenericComponent):

        def __init__(self):
            super(Validation.URLComponent, self).__init__()
            self.component_type_code = 8

        def validate(self, value):
            return value, value

    class FileChooserComponent(GenericComponent):

        def __init__(self):
            super(Validation.FileChooserComponent, self).__init__()
            self.component_type_code = 9

        def validate(self, value):
            return value, value

    class DirectoryChooserComponent(GenericComponent):

        def __init__(self):
            super(Validation.DirectoryChooserComponent, self).__init__()
            self.component_type_code = 10

        def validate(self, value):
            return value, value

    class AttachmentComponent(GenericComponent):

        def __init__(self):
            super(Validation.AttachmentComponent, self).__init__()
            self.component_type_code = 11

        def validate(self, value):
            return value, value

    class PasswordComponent(GenericComponent):

        def __init__(self):
            super(Validation.PasswordComponent, self).__init__()
            self.component_type_code = 12

        def validate(self, value):
            return value, value

    class TableComponent(GenericComponent):

        def __init__(self):
            super(Validation.TableComponent, self).__init__()
            self.component_type_code = 13

        def validate(self, value):
            return value, value

    class BudgetComponent(GenericComponent):

        def __init__(self):
            super(Validation.BudgetComponent, self).__init__()
            self.component_type_code = 14

        def validate(self, value):
            return value, value

    class StaffingProfileComponent(GenericComponent):

        def __init__(self):
            super(Validation.StaffingProfileComponent, self).__init__()
            self.component_type_code = 15

        def validate(self, value):
            return value, value

    class FinancialBenefitComponent(GenericComponent):

        def __init__(self):
            super(Validation.FinancialBenefitComponent, self).__init__()
            self.component_type_code = 18

        def validate(self, value):
            return value, value

    class LinkComponent(GenericComponent):

        def __init__(self):
            super(Validation.LinkComponent, self).__init__()
            self.component_type_code = 19

        def validate(self, value):
            return value, value

    class FinancialSummaryComponent(GenericComponent):

        def __init__(self):
            super(Validation.FinancialSummaryComponent, self).__init__()
            self.component_type_code = 20

        def validate(self, value):
            return value, value

    class ApprovedSnapshotComponent(GenericComponent):

        def __init__(self):
            super(Validation.ApprovedSnapshotComponent, self).__init__()
            self.component_type_code = 21

        def validate(self, value):
            return value, value

    class FinancialDataTableComponent(GenericComponent):

        def __init__(self):
            super(Validation.FinancialDataTableComponent, self).__init__()
            self.component_type_code = 22

        def validate(self, value):
            return value, value

    class AssociatedProgramsComponent(GenericComponent):

        def __init__(self):
            super(Validation.AssociatedProgramsComponent, self).__init__()
            self.component_type_code = 23

        def validate(self, value):
            return value, value

    class PortfolioComponent(GenericComponent):

        def __init__(self):
            super(Validation.PortfolioComponent, self).__init__()
            self.component_type_code = 24

        def validate(self, value):
            return value, value
