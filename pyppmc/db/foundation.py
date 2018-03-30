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

"""Module providing database access to foundation objects.

"""

from pyppmc.foundation import *


class FieldPersister(object):
    """Class to persist field data on database.

    Parameters
    ----------
    session : :[obj]:`Session`, optional
        A valid PPM session.

    """

    def __init__(self, session=None):
        self.session = session

    def get_fields(self, context_id):
        """Retrieves a list of fields defined in the given context_id.

        Parameters
        ----------
        context_id : int
            ID of the context containing the fields.

        Returns
        -------
        list of :[obj]:`Field`
            List of fields on the given context_id.

        """
        cur = self.session.db_con.cursor()
        cur.execute("""\
            SELECT parameter_set_field_id,
                   prompt,
                   description,
                   parameter_token,
                   parameter_column_number,
                   parameter_table_name,
                   validation_id,
                   default_type,
                   default_const_value,
                   visible_default_const_value,
                   section_id,
                   display_flag,
                   display_only_flag,
                   updateable_flag,
                   required_flag,
                   enabled_flag,
                   multi_flag,
                   batch_number,
                   visible_to_all_flag, 
                   editable_by_all_flag,
                   reference_code
            FROM   knta_parameter_set_fields
            WHERE  parameter_set_context_id = :parameter_set_context_id""", parameter_set_context_id=context_id)
        fields = list()
        for row in cur:
            field = Field(persister=self, id=row[0], name=row[3], context_id=context_id, prompt=row[1],
                          description=row[2], column_number=row[4], table_name=row[5], validation_id=row[6],
                          default_type=row[7], default_value=(row[8], row[9]), section_id=row[10],
                          display=(row[11] == 'Y'), display_only=(row[12] == 'Y'), updatable=(row[13] == 'Y'),
                          required=(row[14] == 'Y'), enabled=(row[15] == 'Y'), multi=(row[16] == 'Y'),
                          batch_number=row[17], visible_to_all=(row[18] == 'Y'), editable_by_all=(row[19] == 'Y'),
                          reference_code=row[20])
            fields += [field]
        return fields

    def get(self, id):
        """Retrieves details for the given field.

        Parameters
        ----------
        id : int
            ID of field.

        Returns
        -------
        :[obj]:`Field`
            Field object.

        """
        cur = self.session.db_con.cursor()
        cur.execute("""\
            SELECT parameter_set_field_id,
                   prompt,
                   description,
                   parameter_token,
                   parameter_set_context_id,
                   parameter_column_number,
                   parameter_table_name,
                   validation_id,
                   default_type,
                   default_const_value,
                   visible_default_const_value,
                   section_id,
                   display_flag,
                   display_only_flag,
                   updateable_flag,
                   required_flag,
                   enabled_flag,
                   multi_flag,
                   batch_number,
                   visible_to_all_flag, 
                   editable_by_all_flag,
                   reference_code
            FROM   knta_parameter_set_fields
            WHERE  parameter_set_field_id = :parameter_set_field_id""", parameter_set_field_id=id)
        for row in cur:
            field = Field(persister=self, id=row[0], name=row[3], context_id=row[4], prompt=row[1],
                          description=row[2], column_number=row[5], table_name=row[6], validation_id=row[7],
                          default_type=row[8], default_value=(row[9], row[10]), section_id=row[11],
                          display=(row[12] == 'Y'), display_only=(row[13] == 'Y'), updatable=(row[14] == 'Y'),
                          required=(row[15] == 'Y'), enabled=(row[16] == 'Y'), multi=(row[17] == 'Y'),
                          batch_number=row[18], visible_to_all=(row[19] == 'Y'), editable_by_all=(row[20] == 'Y'),
                          reference_code=row[21])
            return field


class ValidationPersister(object):
    """Class to persist validation data.

    Parameters
    ----------
    session : :[obj]:`Session`, optional
        A valid PPM session.

    """

    def __init__(self, session=None):
        self.session = session

    def get(self, validation_id):
        cur = self.session.db_con.cursor()
        data = dict()
        cur.execute("""\
            SELECT *
            FROM   knta_validations
            WHERE  validation_id = :validation_id""", validation_id=validation_id)
        for row in cur:
            for i, col in enumerate(row):
                data[cur.description[i][0]] = col
        validation = Validation(persister=None, id=data['VALIDATION_ID'], name=data['VALIDATION_NAME'],
                                description=data['DESCRIPTION'], max_length=data['MAX_LENGTH'],
                                enabled=(data['ENABLED_FLAG'] == 'Y'), reference_code=data['REFERENCE_CODE'])

        validation.component = None
        # TODO Implement validation logic for each component type.
        if data['COMPONENT_TYPE_CODE'] == '1':
            validation.component = Validation.TextComponent(data['DATA_MASK_CODE'], data['MAX_LENGTH'])
        elif data['COMPONENT_TYPE_CODE'] == '2':
            validation.component = Validation.DropDownListComponent()
        elif data['COMPONENT_TYPE_CODE'] == '3':
            validation.component = Validation.RadioButtonComponent()
        elif data['COMPONENT_TYPE_CODE'] == '4':
            validation.component = Validation.AutoCompleteListComponent()
        elif data['COMPONENT_TYPE_CODE'] == '5':
            validation.component = Validation.TextAreaComponent()
        elif data['COMPONENT_TYPE_CODE'] == '7':
            validation.component = Validation.DateComponent()
        elif data['COMPONENT_TYPE_CODE'] == '8':
            validation.component = Validation.URLComponent()
        elif data['COMPONENT_TYPE_CODE'] == '9':
            validation.component = Validation.FileChooserComponent()
        elif data['COMPONENT_TYPE_CODE'] == '10':
            validation.component = Validation.DirectoryChooserComponent()
        elif data['COMPONENT_TYPE_CODE'] == '11':
            validation.component = Validation.AttachmentComponent()
        elif data['COMPONENT_TYPE_CODE'] == '12':
            validation.component = Validation.PasswordComponent()
        elif data['COMPONENT_TYPE_CODE'] == '13':
            validation.component = Validation.TableComponent()
        elif data['COMPONENT_TYPE_CODE'] == '14':
            validation.component = Validation.BudgetComponent()
        elif data['COMPONENT_TYPE_CODE'] == '15':
            validation.component = Validation.StaffingProfileComponent()
        elif data['COMPONENT_TYPE_CODE'] == '18':
            validation.component = Validation.FinancialBenefitComponent()
        elif data['COMPONENT_TYPE_CODE'] == '19':
            validation.component = Validation.LinkComponent()
        elif data['COMPONENT_TYPE_CODE'] == '20':
            validation.component = Validation.FinancialSummaryComponent()
        elif data['COMPONENT_TYPE_CODE'] == '21':
            validation.component = Validation.ApprovedSnapshotComponent()
        elif data['COMPONENT_TYPE_CODE'] == '22':
            validation.component = Validation.FinancialDataTableComponent()
        elif data['COMPONENT_TYPE_CODE'] == '23':
            validation.component = Validation.AssociatedProgramsComponent()
        elif data['COMPONENT_TYPE_CODE'] == '24':
            validation.component = Validation.PortfolioComponent()

        return validation
