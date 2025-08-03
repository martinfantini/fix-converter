# Copyright (C) 2025 Roberto Martin Fantini <martin.fantini@gmail.com>
# This file may be distributed under the terms of the GNU GPLv3 license

from typing import Required
from schema import MessageComponent
from definition import FieldDefinition
from typing import Dict
from schema import *
from definition import *
from helpers import *

class DefinitionHelper:

    """ define primiteive data type conversion """
    PRIMITIVE_TYPE_BY_DEFINITION = UniqueKeysDict({
        "LOCALMKTDATE": 'string',
        "STRING": 'string',
        "BOOLEAN": 'bool',
        "EXCHANGE": 'string',
        "PRICE": 'long',
        "QTY": 'int',
        "SEQNUM": 'int',
        "NUMINGROUP": 'int',
        "INT": 'int',
        "FLOAT": 'float',
        "LENGTH": 'int',
        "DATA": 'string',
    })

    def get_value_def(self, parsed_value: Field_Value) -> ValueDefinition:
        return ValueDefinition(
            name = parsed_value.enum,
            value = parsed_value.enum,
            description = parsed_value.description,
        )

    def get_field_def(self, field_parsed: Field) -> FieldDefinition:
        primitive_result =  DefinitionHelper.PRIMITIVE_TYPE_BY_DEFINITION[field_parsed.field_type]
        if primitive_result == None:
            raise Exception(f'Internal Error: unsupported primitive "{field_parsed.field_type}"')
        is_enum_bool = False
        values_dict =  UniqueKeysDict()
        if len(field_parsed.value_by_description) != 0:
            is_enum_bool = True
            for value_parsed in field_parsed.value_by_description.values():
                values_definition_result = self.get_value_def(value_parsed)
                values_dict[values_definition_result.name] = values_definition_result

        return FieldDefinition(
            name = field_parsed.name,
            number = field_parsed.number,
            type = field_parsed.field_type,
            primitive_type = primitive_result,
            is_enum = is_enum_bool,
            values = values_dict,
        )

    def generate_fields_definition(self, field_parsed: Dict[str, Field]) ->  Dict[str, FieldDefinition]:
        fields_definition = UniqueKeysDict()
        for field_value in field_parsed.values():
            fields_definition_result = self.get_field_def(field_value)
            fields_definition[fields_definition_result.name] = fields_definition_result
        return fields_definition

    def get_field_value(self, field_name: str, required_bool: bool, field_parsed: Dict[str, Field]) -> FieldValue:
        if field_parsed[field_name] == None:
            raise Exception(f'Internal Error: unsupported field "{field_name}"')
        return FieldValue(
            name = field_name,
            required = required_bool,
        )

    def get_field_value_from_message_field(self, message_field: MessageField, field_parsed: Dict[str, Field] ) -> FieldValue:
        if field_parsed[message_field.name] == None:
            raise Exception(f'Internal Error: undefined field "{message_field.name}"')
        return FieldValue(name = message_field.name, required = message_field.required)

    def get_group_value_from_message_group(self, message_group: MessageGroup) -> GroupValue:
        return GroupValue(name = message_group.name, required = message_group.required)

    def get_fields_in_component(self, message_component: MessageComponent, actual_component_dict : Dict[str, ComponentValue])-> Dict[int, Union[FieldValue, GroupValue]]:
        fields_in_component = UniqueKeysDict()
        found_component = actual_component_dict[message_component.name]
        if found_component == None:
            raise Exception(f'Internal Error: component "{message_component.name}" undefined or not defined at correct sequence')
        for fields_in_found_component in found_component.fields.values():
            if isinstance(fields_in_found_component, FieldValue):
                fields_in_component[fields_in_found_component.name] = fields_in_found_component
            elif isinstance(fields_in_found_component, GroupValue):
                fields_in_component[fields_in_found_component.name] = GroupValue(
                    name = fields_in_found_component.name,
                    required = fields_in_found_component.required,
                    required_group = message_component.required,
                )
        return fields_in_component

    def generate_component_value(self, component: Component, field_parsed: Dict[str, Field], actual_component_dict : Dict[str, ComponentValue]) -> ComponentValue:
        name_str = component.name
        field_dict = UniqueKeysDict()
        for field_in_component in component.field_group_by_name.values():
            if isinstance(field_in_component, MessageField):
                if field_parsed[field_in_component.name] == None:
                    raise Exception(f'Internal Error: unsupported field "{field_in_component.name}" inside the component "{component.name}"')
                result_field = self.get_field_value_from_message_field(field_in_component, field_parsed)
                field_dict[result_field.name] = result_field
            elif isinstance(field_in_component, MessageGroup):
                if field_parsed[field_in_component.name] == None:
                    raise Exception(f'Internal Error: unsupported group "{field_in_component.name}" inside the component "{component.name}"')
                result_field = self.get_group_value_from_message_group(field_in_component)
                field_dict[result_field.name] = result_field
            elif isinstance(field_in_component, MessageComponent):
                if actual_component_dict[field_in_component.name] == None:
                    raise Exception(f'Internal Error: component "{field_in_component.name}" has to be defined before use it "{component.name}"')
                result_fields =  self.get_fields_in_component(field_in_component, actual_component_dict)
                for result_field in result_fields.values():
                    field_dict[result_field.name] = result_field
        return ComponentValue(name = name_str, fields = field_dict)

    def generate_component_definition(self, component_parsed: Dict[str, Component], field_parsed: Dict[str, Field]) -> Dict[str, ComponentValue]:
        components_dict = UniqueKeysDict()
        for component_data in component_parsed.values():
            component_result =  self.generate_component_value(component_data, field_parsed, components_dict)
            components_dict[component_result.name] = component_result
        return components_dict

    def generate_message_definition(self, parsed_messages: Dict[str, Message], field_parsed: Dict[str, Field], component_definition: Dict[str, ComponentValue]) -> Dict[str, MessageDefinition]:
        messages_dict = UniqueKeysDict()
        for parsed_message in parsed_messages.values():
            message_definition_result = self.get_message_definition(parsed_message, field_parsed, component_definition)
            messages_dict[message_definition_result.name] = message_definition_result
        return messages_dict

    def get_message_definition(self, parsed_message: Message, field_parsed: Dict[str, Field], component_definition: Dict[str, ComponentValue]) -> MessageDefinition:
        fields_dict = UniqueKeysDict()
        for field_message in parsed_message.fields.values():
            if isinstance(field_message, MessageField):
                result_field_value = self.get_field_value_from_message_field(field_message, field_parsed)
                fields_dict[field_parsed[result_field_value.name].number] = result_field_value
            elif isinstance(field_message, MessageGroup):
                result_group_value = self.get_group_value_from_message_group(field_message)
                if field_parsed[result_group_value.name] == None:
                    raise Exception(f'Internal Error: undefined field "{result_group_value.name}"')
                fields_dict[field_parsed[result_group_value.name].number] = GroupValue(
                    name = result_group_value.name,
                    required = result_group_value.required,
                    required_group = result_group_value.required)
            elif isinstance(field_message, MessageComponent):
                result_component_value = self.get_fields_in_component(field_message, component_definition)
                for element_in_component in result_component_value.values():
                    if isinstance(element_in_component, FieldValue):
                        fields_dict[field_parsed[element_in_component.name].number] = element_in_component
                    elif isinstance(element_in_component, GroupValue):
                        if field_parsed[element_in_component.name] == None:
                            raise Exception(f'Internal Error: undefined field "{element_in_component.name}"')
                        fields_dict[field_parsed[element_in_component.name].number] = GroupValue(
                            name = element_in_component.name,
                            required = element_in_component.required,
                            required_group = field_message.required )
        return MessageDefinition(
            name = parsed_message.name,
            msg_type = parsed_message.msg_type,
            msg_category = parsed_message.msg_category,
            fields = fields_dict)

    #def generate_group_definition(self, parsed_messages: Dict[str, Message], component_parsed: Dict[str, Component], field_parsed: Dict[str, Field]) -> Dict[str, GroupDefinition]:
    
    def generate_header(self, header: Header, field_parsed: Dict[str, Field], component_definition: Dict[str, ComponentValue]) -> HeaderDefinition:
        fields_dict = UniqueKeysDict()
        for field_header in header.fields.values():
            if isinstance(field_trailer, MessageField):
                result_field_value = self.get_field_value_from_message_field(field_trailer, field_parsed)
                fields_dict[field_parsed[result_field_value.name].number] = result_field_value
            elif isinstance(field_trailer, MessageGroup):
                result_group_value = self.get_group_value_from_message_group(field_trailer)
                if field_parsed[result_group_value.name] == None:
                    raise Exception(f'Internal Error: undefined field "{result_group_value.name}"')
                fields_dict[field_parsed[result_group_value.name].number] = GroupValue(
                    name = result_group_value.name,
                    required = result_group_value.required,
                    required_group = result_group_value.required)
            elif isinstance(field_trailer, MessageComponent):
                result_component_value = self.get_fields_in_component(field_trailer, component_definition)
                for element_in_component in result_component_value.values():
                    if isinstance(element_in_component, FieldValue):
                        fields_dict[field_parsed[element_in_component.name].number] = element_in_component
                    elif isinstance(element_in_component, GroupValue):
                        if field_parsed[element_in_component.name] == None:
                            raise Exception(f'Internal Error: undefined field "{element_in_component.name}"')
                        fields_dict[field_parsed[element_in_component.name].number] = GroupValue(
                            name = element_in_component.name,
                            required = element_in_component.required,
                            required_group = field_trailer.required )
        return fields_dict

    def generate_trailer(self, trailer: Trailer, field_parsed: Dict[str, Field], component_definition: Dict[str, ComponentValue]) -> TrailerDefinition:
        fields_dict = UniqueKeysDict()
        for field_trailer in trailer.fields.values():
            if isinstance(field_trailer, MessageField):
                result_field_value = self.get_field_value_from_message_field(field_trailer, field_parsed)
                fields_dict[field_parsed[result_field_value.name].number] = result_field_value
            elif isinstance(field_trailer, MessageGroup):
                result_group_value = self.get_group_value_from_message_group(field_trailer)
                if field_parsed[result_group_value.name] == None:
                    raise Exception(f'Internal Error: undefined field "{result_group_value.name}"')
                fields_dict[field_parsed[result_group_value.name].number] = GroupValue(
                    name = result_group_value.name,
                    required = result_group_value.required,
                    required_group = result_group_value.required)
            elif isinstance(field_trailer, MessageComponent):
                result_component_value = self.get_fields_in_component(field_trailer, component_definition)
                for element_in_component in result_component_value.values():
                    if isinstance(element_in_component, FieldValue):
                        fields_dict[field_parsed[element_in_component.name].number] = element_in_component
                    elif isinstance(element_in_component, GroupValue):
                        if field_parsed[element_in_component.name] == None:
                            raise Exception(f'Internal Error: undefined field "{element_in_component.name}"')
                        fields_dict[field_parsed[element_in_component.name].number] = GroupValue(
                            name = element_in_component.name,
                            required = element_in_component.required,
                            required_group = field_trailer.required )
        return fields_dict
