# Copyright (C) 2025 Roberto Martin Fantini <martin.fantini@gmail.com>
# This file may be distributed under the terms of the GNU GPLv3 license

from app.definition import *
from abc import ABC, abstractmethod

class GeneratorBase(ABC):

    @abstractmethod
    def _generate_impl(self, schema: dict) -> None:
        pass

    def generate(self, schema_definition: SchemaDefinition) -> None:
        ir = {}
        ir['package'] = schema_definition.package
        ir['version'] = schema_definition.version
        ir['fix_version_major'] = str(schema_definition.fix_major_version)
        ir['fix_version_minor'] = str(schema_definition.fix_minor_version)

        # field definition
        ir['fields'] = []
        for field_definition in schema_definition.fields.values():
            ir['fields'].append(GeneratorBase.make_field_definition(field_definition))

        # group definition
        ir['groups'] = []
        for group_definition in schema_definition.groups.values():
            ir['groups'].append(GeneratorBase.make_group_definition(group_definition, schema_definition.fields))

        # header definition
        ir['header'] = []
        if schema_definition.header != None:
            ir['header'].append(GeneratorBase.make_header_definition(schema_definition.header, schema_definition.fields))

        # trailer definition
        ir['trailer'] = []
        if schema_definition.trailer != None:
            ir['trailer'].append(GeneratorBase.make_trailer_definition(schema_definition.trailer, schema_definition.fields))

        # messages definition
        ir['messages'] = []
        for message_definition in schema_definition.messages.values():
            ir['messages'].append(GeneratorBase.make_message_definition(message_definition, schema_definition.fields))

        self._generate_impl(ir)

    @staticmethod
    def make_field_definition(field_definition: FieldDefinition) -> dict:
        if len(field_definition.values) == 1 and field_definition.is_enum == True:
            token_str = 'const'
        elif len(field_definition.values) > 1 and field_definition.is_enum == True:
            token_str = 'enum'
        elif field_definition.is_enum == False:
            token_str = 'data'
        else:
            raise Exception(f'Internal Error: wrong defined field definition "{field_definition.name}", number of values "{len(field_definition.values)}" and is_enum flag {str(field_definition.is_enum)}')

        values_dict = []
        for value_definition in field_definition.values.values():
            values_dict.append(GeneratorBase.make_values_definition(value_definition))
            
        return {
            'token': token_str,
            'name': field_definition.name,
            'number': field_definition.number,
            'type': field_definition.type,
            'primitive_type': field_definition.primitive_type,
            'values': values_dict
        }

    @staticmethod
    def make_values_definition(value_definition: ValueDefinition) -> dict:
        return {
            'name' : value_definition.description,
            'value' : value_definition.value
        }

    @staticmethod
    def generate_fields_list_by_parsed_order(fields_definition_dict: Dict[int, Union[FieldValue, GroupValue]], fields_definition: Dict[str, FieldDefinition]):
        fields_list  = []
        for field in fields_definition_dict:
            if isinstance(field[1], GroupValue):
                fields_list.append(GeneratorBase.make_group_definition_in_group(field[1], field[0], fields_definition))
            elif isinstance(field[1], FieldValue):
                fields_list.append(GeneratorBase.make_field_definition_in_group(field[1], field[0], fields_definition))
        return fields_list

    @staticmethod
    def generate_fields_list_by_id(fields_definition_dict: Dict[int, Union[FieldValue, GroupValue]], fields_definition: Dict[str, FieldDefinition]):
        fields_list  = []
        sorted_dictionary = sorted(fields_definition_dict.items(), key=lambda x: str(x[0]))
        for field in sorted_dictionary:
            if isinstance(field[1], GroupValue):
                fields_list.append(GeneratorBase.make_group_definition_in_group(field[1], field[0], fields_definition))
            elif isinstance(field[1], FieldValue):
                fields_list.append(GeneratorBase.make_field_definition_in_group(field[1], field[0], fields_definition))
        return fields_list

    @staticmethod
    def make_group_definition(group_definition: GroupDefinition, fields_definition: Dict[str, FieldDefinition] ) -> dict:
        number_of_elements_field = fields_definition[group_definition.number_element_field.name]
        if number_of_elements_field == None:
            raise Exception(f'Internal Error: field "{number_of_elements_field.name}" not defined')
        start_group_field = fields_definition[group_definition.start_group_field.name]
        if start_group_field == None:
            raise Exception(f'Internal Error: field "{start_group_field.name}" not defined')

        return {
            'token': 'group',
            'name': group_definition.name,
            'number_of_elements': group_definition.number_element_field.name,
            'number_of_elements_id': str(number_of_elements_field.number),
            'start_group_field': start_group_field.name,
            'start_group_field_id': str(start_group_field.number),
            'fields_by_id': GeneratorBase.generate_fields_list_by_id(group_definition.fields, fields_definition),
            'fields_by_order': GeneratorBase.generate_fields_list_by_parsed_order(group_definition.fields, fields_definition),
        }

    @staticmethod
    def make_group_definition_in_group(group_definition: GroupValue, group_id: int, fields_definition: Dict[str, FieldDefinition]) -> dict:
        if fields_definition[group_definition.name] == None:
            raise Exception(f'Internal Error: field "{group_definition.name}" not defined')

        return {
            'token': 'group',
            'name': group_definition.name,
            'required': str(group_definition.required_group),
            'id': group_id,
        }

    @staticmethod
    def make_field_definition_in_group(field_definition: FieldValue, field_id: int, fields_definition: Dict[str, FieldDefinition]) -> dict:
        if fields_definition[field_definition.name] == None:
            raise Exception(f'Internal Error: field "{field_definition.name}" not defined')

        return {
            'token': 'field',
            'name': field_definition.name,
            'required': field_definition.required,
            'id': field_id,
        }

    @staticmethod
    def make_trailer_definition(trailer: TrailerDefinition, fields_definition: Dict[str, FieldDefinition]) -> dict:
        return {
            'token': 'trailer',
            'fields_by_id': GeneratorBase.generate_fields_list_by_id(trailer.fields, fields_definition),
            'fields_by_order': GeneratorBase.generate_fields_list_by_parsed_order(trailer.fields, fields_definition),
        }

    @staticmethod
    def make_header_definition(header: HeaderDefinition, fields_definition: Dict[str, FieldDefinition]) -> dict:
        return {
            'token': 'header',
            'fields_by_id': GeneratorBase.generate_fields_list_by_id(header.fields, fields_definition),
            'fields_by_order': GeneratorBase.generate_fields_list_by_parsed_order(header.fields, fields_definition),
        }

    @staticmethod
    def make_message_definition(message_definition: MessageDefinition, fields_definition: Dict[str, FieldDefinition]) -> dict:
        return {
            'token': 'message',
            'name': message_definition.name,
            'type': message_definition.msg_type,
            'fields_by_id': GeneratorBase.generate_fields_list_by_id(message_definition.fields, fields_definition),
            'fields_by_order': GeneratorBase.generate_fields_list_by_parsed_order(message_definition.fields, fields_definition),
        }
