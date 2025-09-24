# Copyright (C) 2025 R. Martin Fantini <martin.fantini@gmail.com>
# This file may be distributed under the terms of the GNU GPLv3 license

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Union

@dataclass(frozen=True)
class ValueDefinition:
    name: str = field(default_factory=str)
    value: str = field(default_factory=str)
    description: str = field(default_factory=str)

@dataclass(frozen=True)
class FieldDefinition:
    name: str = field(default_factory=str)
    number: Optional[int] = field(default=None)
    type: str = field(default_factory=str)
    primitive_type: str = field(default_factory=str)
    is_enum: bool = field(default=False)
    values: Dict[str, ValueDefinition] = field(default_factory=dict)

@dataclass(frozen=True)
class GroupDefinition:
    name: str = field(default_factory=str)
    number_element_field: FieldValue = field(default=None)
    start_group_field: Union[FieldValue, GroupValue] = field(default=None)
    fields: Dict[int, Union[FieldValue, GroupValue]] = field(default_factory=dict)
    fields_by_tree: TreeDefinition = field(default=None)

@dataclass
class FieldValue:
    name: str = field(default_factory=str)
    required: bool = field(default=False)
    is_begin_message: bool = field(default=False)
    is_end_message: bool = field(default=False)

    def set_begin_message(self):
        self.is_begin_message = True

    def set_end_message(self):
        self.is_end_message = True

@dataclass(frozen=True)
class GroupValue:
    name: str = field(default_factory=str)
    required: bool = field(default=False)
    required_group: bool = field(default=False)

@dataclass(frozen=True)
class ComponentValue:
    name: str = field(default_factory=str)
    fields: Dict[int, Union[FieldValue, GroupValue]] = field(default_factory=dict)

@dataclass(frozen=True)
class MessageDefinition:
    name: str = field(default_factory=str)
    msg_type: str = field(default_factory=str)
    msg_category: Optional[str] = field(default=None)
    fields: Dict[int, Union[FieldValue, GroupValue]] = field(default_factory=dict)
    fields_by_tree: TreeDefinition = field(default=None)

@dataclass(frozen=True)
class HeaderDefinition:
    fields: Dict[int, Union[FieldValue, GroupValue]] = field(default_factory=dict)

@dataclass(frozen=True)
class TrailerDefinition:
    fields: Dict[int, Union[FieldValue, GroupValue]] = field(default_factory=dict)

@dataclass(frozen=True)
class SchemaDefinition:
    fields: Dict[str, FieldDefinition] = field(default_factory=dict)
    groups: Dict[str, GroupDefinition] = field(default_factory=dict)
    messages: Dict[str, MessageDefinition] = field(default_factory=dict)
    header: HeaderDefinition = field(default=None)
    trailer: TrailerDefinition = field(default=None)
    fix_minor_version: int = field(default=0)
    fix_major_version: int = field(default=0)
    package: Optional[str] = field(default=None)
    version: Optional[str] = field(default=None)

class TreeDefinition:
    def __init__(self):
        self.value = None
        self.tree_ids = dict()
        self.depth = 1

    def find(self, id_field: str) -> bool:
        if id_field in self.tree_ids:
            return True
        return False

    def add_value(self, value: Union[FieldValue, GroupValue]):
        self.value = value

    def add_sub_node(self, id_field: str, node):
        self.tree_ids[id_field] = node
