# Copyright (C) 2025 R. Martin Fantini <martin.fantini@gmail.com>
# This file may be distributed under the terms of the GNU GPLv3 license

from __future__ import annotations
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Union, Tuple
from collections import UserDict
from schema import *
from xml_helper import *

class UniqueKeysDict(UserDict):
    def __setitem__(self, key, value):
        if key in self.data:
            raise Exception(f'duplicate key "{key}"')
        self.data[key] = value

class Parser:

    def __init__(self, root: ET.Element) -> None:
        self.root = root

    @staticmethod
    def from_file(path: str) -> Parser:
        root = load_xml_from_file(path)
        return Parser(root)

    @staticmethod
    def from_string(string_xml: str) -> Parser:
        root = load_xml_from_string(string_xml)
        return Parser(root)

    # <value enum="L" description="LESSEE"/>
    def parse_enum_value(self, node: ET.Element) -> Field_Value:
        return Field_Value(
            enum = attr(node, 'enum'),
            description = attr(node, 'description'),
        )

    #   <field number="9706" name="FeeBilling" type="CHAR">
    #      <value enum="B" description="CBOE_MEMBER"/>
    #      <value enum="C" description="CUSTOMER"/>
    #      <value enum="E" description="EQUITY_MEMBER"/>
    #      <value enum="H" description="FIRM"/>
    #      <value enum="L" description="LESSEE"/>
    #   </field>
    def parse_field(self, node: ET.Element) -> Field:
        name_str = attr(node, 'name')
        field_type_str = attr(node, 'type')
        number_int = attr(node, 'number')
        if number_int == None:
            raise Exception(f'Malformed XML: The field "{name_str}" has no number "{number_int}"')
        value_by_description_dict = UniqueKeysDict()
        for child in node:
            if child.tag == 'value':
                member_value = self.parse_enum_value(child)
                value_by_description_dict[member_value.description] = member_value
        return Field(
            name = name_str,
            number = number_int,
            field_type = field_type_str,
            value_by_description = value_by_description_dict,
        )

    #    <field name="CheckSum" required="Y"/>
    def parse_message_field(self, node: ET.Element, dict_fields: Dict[str, Field]) -> MessageField:
        name_str = attr(node, 'name')
        if dict_fields[name_str] == None:
            raise Exception(f'Malformed XML: the field "{name_str}" is not present in the field dictionary')
        required_bool = attr(node, 'required')
        return MessageField(
            name = name_str,
            required = required_bool,
        )

    #   <group name="NoQuoteEntries">
    #      <field name="Symbol"/>
    #      <field name="SecurityDesc"/>
    #   </group>
    # or
    #   <group name="NoRiskLimitTypes" required="Y">
    #       <field name="RiskLimitType" required="Y" />
    #   </group>
    def parse_message_group(self, node: ET.Element, dict_fields: Dict[str, Field]) -> MessageGroup:
        name_str = attr(node, 'name')
        required_bool: Any = attr(node, 'required')
        field_by_name_dict = UniqueKeysDict()
        for child in node:
            if child.tag == 'field':
                child_field = self.parse_message_field(child, dict_fields)
                field_by_name_dict[child_field.name] = child_field

        return MessageGroup(
           name = name_str,
           required = required_bool,
           field_by_name = field_by_name_dict,
        )

    #    <component name="QuotEntryGrp">
    #      <field name="SecurityDesc"/>
    #      <group name="NoQuoteEntries">
    #        <field name="QuoteEntryID"/>
    #        <field name="Symbol"/>
    #        <field name="SecurityDesc"/>
    #        <field name="SecurityType"/>
    #        <field name="SecurityID"/>
    #        <field name="SecurityIDSource"/>
    #        <field name="TransactTime"/>
    #        <field name="BidPx"/>
    #        <field name="BidSize"/>
    #        <field name="OfferPx"/>
    #        <field name="OfferSize"/>
    #      </group>
    #    </component>
    # or
    #    <component name="RiskLimitTypesGrp">
    #       <group name="NoRiskLimitTypes" required="Y">
    #           <field name="RiskLimitType" required="Y" />
    #       </group>
    #   </component>
    def parse_message_component(self, node: ET.Element, dict_fields: Dict[str, Field]) -> MessageComponent:
        name_str= attr(node, 'name')
        field_group_by_name_dict = UniqueKeysDict()
        for child in node:
            if child.tag == 'group':
                child_group = self.parse_message_group(child, dict_fields)
                field_group_by_name_dict[child_group.name] = child_group
            elif child.tag == 'field':
                child_field = self.parse_message_field(child, dict_fields)
                field_group_by_name_dict[child_field.name] = child_field
            else:
                raise Exception(f'Malformed XML: unsupported tag "{child.tag}" in the component definition')

        return MessageComponent(
            name = name_str,
            field_group_by_name = field_group_by_name_dict
        )

    #        <message name="UserPartyRiskLimitsRequest" msgtype="UCL" msgcat="app">
    #        	<component name="Parties" required="Y" />
    #        	<field name="MarketSegmentID" required="Y" />
    #        	<field name="RiskLimitRequestID" required="Y" />
    #        	<field name="RiskLimitGroup" required="N" />
    #        </message>
    # or
    #        <message name="OrderCancelReplaceRequest" msgtype="G">
    def parse_message(self, node: ET.Element, dict_fields: Dict[str, Field]) -> Message:
        name_str= attr(node, 'name')
        msg_type_str= attr(node, 'msgtype')
        msg_category_str= attr(node, 'msgcat')
        fields_dict = UniqueKeysDict()
        for child in node:
            if child.tag == 'group':
                child_group = self.parse_message_group(child, dict_fields)
                fields_dict[child_group.name] = child_group
            elif child.tag == 'field':
                child_field = self.parse_message_field(child, dict_fields)
                fields_dict[child_field.name] = child_field
            elif child.tag == 'component':
                child_component  = self.parse_message_component(child, dict_fields)
                fields_dict[child_component.name] = child_component
            else:
                raise Exception(f'Malformed XML: unsupported tag "{child.tag}" in the message definition')

        return Message(
            name = name_str,
            msg_type = msg_type_str,
            msg_category = msg_category_str,
            fields = fields_dict,
        )

    #  <trailer>
    #    <field name="CheckSum" required="Y"/>
    #  </trailer>
    def parse_trailer(self, node: ET.Element, dict_fields: Dict[str, Field]) -> Trailer:
        fields_dict = UniqueKeysDict()
        for child in node:
            if child.tag == 'group':
                child_group = self.parse_message_group(child, dict_fields)
                fields_dict[child_group.name] = child_group
            elif child.tag == 'field':
                child_field = self.parse_message_field(child, dict_fields)
                fields_dict[child_field.name] = child_field
            elif child.tag == 'component':
                child_component  = self.parse_message_component(child, dict_fields)
                fields_dict[child_component.name] = child_component
            else:
                raise Exception(f'Malformed XML: unsupported tag "{child.tag}" in the Trailer definition')

        return Trailer(fields = fields_dict)

    #  <header>
    #    <field name="BeginString" required="Y" />
    #  </header>
    #    or 
    #  <header>
    #    <field name="BeginString"/>
    #  </header>
    def parse_header(self, node: ET.Element, dict_fields: Dict[str, Field]) -> Header:
        fields_dict = UniqueKeysDict()
        for child in node:
            if child.tag == 'group':
                child_group = self.parse_message_group(child, dict_fields)
                fields_dict[child_group.name] = child_group
            elif child.tag == 'field':
                child_field = self.parse_message_field(child, dict_fields)
                fields_dict[child_field.name] = child_field
            elif child.tag == 'component':
                child_component  = self.parse_message_component(child, dict_fields)
                fields_dict[child_component.name] = child_component
            else:
                raise Exception(f'Malformed XML: unsupported tag "{child.tag}" in the Header definition')
        return Header(fields = fields_dict)

    def get_fields(self) -> Dict[str, Field]:
        fields_dict = UniqueKeysDict()
        for child_field_definition in self.root.findall("fix/fields/field"):
            result_field = self.parse_field(child_field_definition)
            fields_dict[result_field.name] = result_field
        return fields_dict

    def get_components(self, dict_fields: Dict[str, Field]) -> Dict[str, MessageComponent]:
        component_dict = UniqueKeysDict()
        for child_component_definition in self.root.findall("fix/components/component"):
            result_component = self.parse_message_component(child_component_definition, dict_fields)
            component_dict[result_component.name] = result_component
        return component_dict

    def get_messages(self, dict_fields: Dict[str, Field]) -> Dict[str, Message]:
        message_dict = UniqueKeysDict()
        for child_message_definition in self.root.findall("fix/messages/message"):
            result_message = self.parse_message(child_message_definition, dict_fields)
            message_dict[result_message.name] = result_message
        return message_dict

    def get_header(self, dict_fields: Dict[str, Field]) -> Header:
        header = None
        for header_definition in self.root.findall("fix/header"):
            header = self.parse_header(header_definition, dict_fields)
        if header == None:
            raise Exception(f'Malformed XML: header is not present')
        return header

    def get_trailer(self, dict_fields: Dict[str, Field]) -> Trailer:
        trailer = None
        for trailer_definition in self.root.findall("fix/trailer"):
            trailer = self.parse_trailer(trailer_definition, dict_fields)
        return trailer

    #<fix major="4"
    #     minor="4"
    #     copyright="Copyright (C) 2022 Deutsche Boerse AG. All rights reserved."
    #     version="131.430.0.ga-131004030-27">
    #or 
    #
    #    <fix major="4" minor="2">
    def parse_schema(self)
        major_version_int = 0
        minor_version_int = 0
        for child_fix_definition in self.root.findall("fix"):
            major_version_int = attr(child_fix_definition, 'major')
            minor_version_int = attr(child_fix_definition, 'minor')
            cpyrght_str = attr(child_fix_definition, 'copyright')
            vrsn_str = attr(child_fix_definition, 'version')

        if major_version_int == 0 or minor_version_int == 0:
            raise Exception(f'Malformed XML: major or minor version is not present')

        fields_dict = self.get_fields()
        components_dict = self.get_components(fields_dict)
        message_dict = self.get_messages(fields_dict)
        header_def = self.get_header(fields_dict)
        trailer_def = self.get_trailer(fields_dict)

        return Schema(
            major_version = major_version_int,
            minor_version = minor_version_int,
            copyright_str = cpyrght_str,
            version_str = vrsn_str,
            fields = fields_dict,
            components = components_dict,
            message = message_dict,
            header = header_def,
            trailer = trailer_def,
        )

