# Copyright (C) 2025 Roberto Martin Fantini <martin.fantini@gmail.com>
# This file may be distributed under the terms of the GNU GPLv3 license

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Optional
from schema import *
from collections import UserDict

class GeneratorBase(ABC):
    @abstractmethod
    def _generate_impl(self, schema: dict) -> None:
        pass

    def generate(self, schema: Schema) -> None:
        ir = {}
        ir['package'] = schema.name
        ir['version'] = schema.name
        ir['fix_version_major'] = schema.version
        ir['fix_version_minor'] = schema.version

        # field definition
        ir['fields'] = []
        for member_or_group in schema.groups.values():
            ir['groups'].append(GeneratorBase.make_group_definition(member_or_group))

        # group definition
        ir['groups'] = []
        for member_or_group in schema.groups.values():
            ir['groups'].append(GeneratorBase.make_group_definition(member_or_group))

        # messages definition
        ir['header'] = []

        ir['trailer'] = []

        # messages definition
        ir['messages'] = []
        for message_application in schema.application_messages.values():
            ir['messages'].append(GeneratorBase.make_message_definition(message_application))

        self._generate_impl(ir)

    @staticmethod
    def make_data_definition(data_type: DataType) -> dict:
        return {
            'token': 'data',
            'name': data_type.name,
            'type': data_type.basic_type,
            'numeric_id': data_type.numeric_id,
            'size': data_type.primitive_size,
            'description': data_type.description,
            'min_value': data_type.min_value,
            'max_value': data_type.max_value,
            'range': data_type.range,
            'no_value': data_type.no_value,
        }

    @staticmethod
    def make_enum_definition(data_type: DataType) -> dict:
        valid_values = []
        if data_type.has_valid_values:
            for enum_element in data_type.valid_value_by_name.values():
                valid_values.append({
                    'name', enum_element.name,
                    'value', enum_element.value,
                    'description', enum_element.description,
                })

        return {
            'token': 'enum',
            'name': data_type.name,
            'type': data_type.basic_type,
            'numeric_id': data_type.numeric_id,
            'size': data_type.primitive_size,
            'description': data_type.description,
            'min_value': data_type.min_value,
            'max_value': data_type.max_value,
            'range': data_type.range,
            'no_value': data_type.no_value,
            'valid_values': valid_values,
        }

    @staticmethod
    def make_group_definition(group_dinition: ApplicationMessage_Group):
        members = []
        offset_in_group = 0
        for member_of_group in group_dinition.members.values():
            members.append({
                'token': 'member',
                'name': member_of_group.name,
                'hiden': member_of_group.hidden,
                'offset_in_group': offset_in_group,
                'usage': str(member_of_group.usage),
                'cardinality': member_of_group.cardinality,
            })
            offset_in_group += member_of_group.primitive_size
        return{
            'token': 'group',
            'name': group_dinition.name,
            'group_name': group_dinition.group_type,
            'cardinality': group_dinition.cardinality,
            'counter':  group_dinition.counter,
            'group_size': group_dinition.primitive_size,
            'members': members,
        }

    @staticmethod
    def make_message_definition(application_message: ApplicationMessage) -> dict:
        members = []
        for member_or_group in application_message.members_or_groups:
            if isinstance(member_or_group, ApplicationMessage_Member):
                entry = GeneratorBase.make_aplication_member_definition(member_or_group)
            elif isinstance(member_or_group, ApplicationMessage_Group):
                entry = GeneratorBase.make_aplication_group_definition(member_or_group)
            members.append(entry)

        return {
            'token': 'message',
            'name': application_message.name,
            'numeric_id': application_message.numeric_id,
            'message_size': application_message.primitive_size,
            'members': members
        }

    @staticmethod
    def make_aplication_member_definition(member: ApplicationMessage_Member):
        constant_enum_value_bool = False
        enum_value_int = None
        if len(member.valid_value_by_name) == 1:
            constant_enum_value_bool = True
            enum_value_int = list(member.valid_value_by_name.values())[0].value

        return{
            'token': 'member',
            'name': member.name,
            'data_type_name': member.member_type,
            'usage': str(member.usage),
            'offset': member.offset,
            'cardinality': member.cardinality,
            'offset_base': member.offset_base,
            'constant_enum_value': constant_enum_value_bool,
            'value': enum_value_int,
        }

    @staticmethod
    def make_aplication_group_definition(member: ApplicationMessage_Group):
        return{
            'token': 'group',
            'name': member.name,
            'group_name': member.group_type,
            'cardinality': member.cardinality,
            'counter':  member.counter,
        }
