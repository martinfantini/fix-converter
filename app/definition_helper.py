# Copyright (C) 2025 Roberto Martin Fantini <martin.fantini@gmail.com>
# This file may be distributed under the terms of the GNU GPLv3 license

from definition import GroupValue
from typing import Required
from schema import MessageComponent
from definition import FieldDefinition
from typing import Dict
from schema import *
from definition import *
from helpers import *
from typing import Dict, Union

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
        "PADDEDSEQNUM": 'int',
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
        fields_dict = self.generate_field_group_values_from_field_component_group(parsed_message.fields, field_parsed, component_definition)
        return MessageDefinition(
            name = parsed_message.name,
            msg_type = parsed_message.msg_type,
            msg_category = parsed_message.msg_category,
            fields = fields_dict)

    def generate_header(self, header: Header, field_parsed: Dict[str, Field], component_definition: Dict[str, ComponentValue]) -> HeaderDefinition:
        fields_dict = self.generate_field_group_values_from_field_component_group(header.fields, field_parsed, component_definition)
        return HeaderDefinition(fields = fields_dict)

    def generate_trailer(self, trailer: Trailer, field_parsed: Dict[str, Field], component_definition: Dict[str, ComponentValue]) -> TrailerDefinition:
        fields_dict = self.generate_field_group_values_from_field_component_group(trailer.fields, field_parsed, component_definition)
        return TrailerDefinition(fields = fields_dict)

    def generate_field_group_values_from_field_component_group(self, fields: Dict[str, Union[MessageField, MessageComponent, MessageGroup]], field_parsed: Dict[str, Field], component_definition: Dict[str, ComponentValue]) -> Dict[int, Union[FieldValue, GroupValue]]:
        fields_dict = UniqueKeysDict()
        for field_element in fields.values():
            if isinstance(field_element, MessageField):
                result_field_value = self.get_field_value_from_message_field(field_element, field_parsed)
                fields_dict[field_parsed[result_field_value.name].number] = result_field_value
            elif isinstance(field_element, MessageGroup):
                result_group_value = self.get_group_value_from_message_group(field_element)
                if field_parsed[result_group_value.name] == None:
                    raise Exception(f'Internal Error: undefined field "{result_group_value.name}"')
                fields_dict[field_parsed[result_group_value.name].number] = GroupValue(
                    name = result_group_value.name,
                    required = result_group_value.required,
                    required_group = result_group_value.required)
            elif isinstance(field_element, MessageComponent):
                result_component_value = self.get_fields_in_component(field_element, component_definition)
                for element_in_component in result_component_value.values():
                    if isinstance(element_in_component, FieldValue):
                        fields_dict[field_parsed[element_in_component.name].number] = FieldValue(name = element_in_component.name, required = field_element.required)
                    elif isinstance(element_in_component, GroupValue):
                        if field_parsed[element_in_component.name] == None:
                            raise Exception(f'Internal Error: undefined field "{element_in_component.name}"')
                        fields_dict[field_parsed[element_in_component.name].number] = GroupValue(
                            name = element_in_component.name,
                            required = element_in_component.required,
                            required_group = field_element.required)
        return fields_dict

    def get_group_definition_from_message_group(self, message_group: MessageGroup, field_parsed: Dict[str, Field], component_definition: Dict[str, ComponentValue]) -> GroupDefinition:
        number_element_field_field_value = self.get_field_value(message_group.name, message_group.required, field_parsed)
        fields_in_group = self.generate_field_group_values_from_field_component_group(message_group.field_by_name, field_parsed, component_definition)
        start_value = list(fields_in_group.values())[0]
        if isinstance(start_value, FieldValue):
            start_group_field_field_value = start_value
        else:
            raise Exception(f'Internal Error: field "{start_value.name}" has to be Field')
        fields_in_group_by_number_by_number = UniqueKeysDict()
        for field_element in fields_in_group.values():
            fields_in_group_by_number_by_number[field_parsed[field_element.name].number] = field_element
            result_group_definition = GroupDefinition(
                    name = message_group.name,
                    number_element_field = number_element_field_field_value,
                    start_group_field = start_group_field_field_value,
                    fields = fields_in_group_by_number_by_number)
        return result_group_definition

    def get_group_definition_from_component(self, parsed_component: Component, field_parsed: Dict[str, Field], component_definition: Dict[str, ComponentValue]) -> GroupDefinition:
        ''' OBSERVATION: for the case of the components, there have ONLY one group per component, for the case of the more than one it is necessary define a component '''
        result_group_definition = None
        for component_element in parsed_component.field_group_by_name.values():
            if isinstance(component_element, MessageGroup):
                result_group_definition = self.get_group_definition_from_message_group(component_element, field_parsed, component_definition)
        return result_group_definition

    def get_group_definition_from_message(self, parsed_message: Message, field_parsed: Dict[str, Field], component_definition: Dict[str, ComponentValue]) -> GroupDefinition:
        ''' OBSERVATION: for the case of the message, there have ONLY one group per component, for the case of the more than one it is necessary define a component '''
        result_group_definition = None
        for message_element in parsed_message.fields.values():
            if isinstance(message_element, MessageGroup):
                result_group_definition = self.get_group_definition_from_message_group(message_element, field_parsed, component_definition)
        return result_group_definition

    def generate_group_definition(self, component_parsed: Dict[str, Component], parsed_messages: Dict[str, Message], field_parsed: Dict[str, Field], component_definition: Dict[str, ComponentValue]) -> Dict[str, GroupDefinition]:
        group_dict =  UniqueKeysDict()
        for component_element in component_parsed.values():
            result_group_definition = self.get_group_definition_from_component(component_element, field_parsed, component_definition)
            if result_group_definition == None:
                continue
            group_dict[result_group_definition.name] = result_group_definition
        for message_element in parsed_messages.values():
            result_group_definition = self.get_group_definition_from_message(message_element, field_parsed, component_definition)
            if result_group_definition == None:
                continue
            group_dict[result_group_definition.name] = result_group_definition
        return group_dict
