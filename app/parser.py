# Copyright (C) 2025 R. Martin Fantini <martin.fantini@gmail.com>
# This file may be distributed under the terms of the GNU GPLv3 license

from __future__ import annotations
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Union, Tuple
from app.schema import *
from app.xml_helper import *
from app.helpers import *

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
        required_bool = attr(node, 'required', "N") == "Y"
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
    def parse_message_group(self, node: ET.Element, dict_fields: Dict[str, Field], dict_components: Dict[str, Component]) -> MessageGroup:
        name_str = attr(node, 'name')
        required_bool = attr(node, 'required', "N") == "Y"
        field_by_name_dict = UniqueKeysDict()
        for child in node:
            if child.tag == 'group':
                child_group = self.parse_message_group(child, dict_fields, dict_components)
                field_by_name_dict[child_group.name] = child_group
            elif child.tag == 'field':
                child_field = self.parse_message_field(child, dict_fields)
                field_by_name_dict[child_field.name] = child_field
            elif child.tag == 'component':
                child_component  = self.parse_message_component(child, dict_components)
                field_by_name_dict[child_component.name] = child_component
            else:
                raise Exception(f'Malformed XML: unsupported tag "{child.tag}" in the group definition')

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
    def parse_component(self, node: ET.Element, dict_fields: Dict[str, Field]) -> Component:
        name_str= attr(node, 'name')
        field_group_by_name_dict = UniqueKeysDict()
        for child in node:
            if child.tag == 'group':
                child_group = self.parse_message_group(child, dict_fields, None)
                field_group_by_name_dict[child_group.name] = child_group
            elif child.tag == 'field':
                child_field = self.parse_message_field(child, dict_fields)
                field_group_by_name_dict[child_field.name] = child_field
            elif child.tag == 'component':
                child_component = self.parse_message_component(child, None)
                field_group_by_name_dict[child_component.name] = child_component
            else:
                raise Exception(f'Malformed XML: unsupported tag "{child.tag}" in the component definition')

        return Component(
            name = name_str,
            field_group_by_name = field_group_by_name_dict
        )

    def parse_message_component(self, node: ET.Element, dict_components: Dict[str, Component]) -> MessageComponent:
        name_str= attr(node, 'name')
        if dict_components != None and dict_components.get(name_str) == None:
            raise Exception(f'Malformed XML: undefined component "{name_str}"')
        required_bool = attr(node, 'required', "N") == "Y"
        return MessageComponent(
            name = name_str,
            required = required_bool,
        )

    #        <message name="UserPartyRiskLimitsRequest" msgtype="UCL" msgcat="app">
    #        	<component name="Parties" required="Y" />
    #        	<field name="MarketSegmentID" required="Y" />
    #        	<field name="RiskLimitRequestID" required="Y" />
    #        	<field name="RiskLimitGroup" required="N" />
    #        </message>
    # or
    #        <message name="OrderCancelReplaceRequest" msgtype="G">
    def parse_message(self, node: ET.Element, dict_fields: Dict[str, Field], dict_components: Dict[str, Component]) -> Message:
        name_str= attr(node, 'name')
        msg_type_str= attr(node, 'msgtype')
        msg_category_str= attr(node, 'msgcat', "")
        fields_dict = UniqueKeysDict()
        for child in node:
            if child.tag == 'group':
                child_group = self.parse_message_group(child, dict_fields, dict_components)
                fields_dict[child_group.name] = child_group
            elif child.tag == 'field':
                child_field = self.parse_message_field(child, dict_fields)
                fields_dict[child_field.name] = child_field
            elif child.tag == 'component':
                child_component  = self.parse_message_component(child, dict_components)
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
    def parse_trailer(self, node: ET.Element, dict_fields: Dict[str, Field], dict_components: Dict[str, Component]) -> Trailer:
        fields_dict = UniqueKeysDict()
        for child in node:
            if child.tag == 'group':
                child_group = self.parse_message_group(child, dict_fields, dict_components)
                fields_dict[child_group.name] = child_group
            elif child.tag == 'field':
                child_field = self.parse_message_field(child, dict_fields)
                fields_dict[child_field.name] = child_field
            elif child.tag == 'component':
                child_component  = self.parse_message_component(child, dict_components)
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
    def parse_header(self, node: ET.Element, dict_fields: Dict[str, Field], dict_components: Dict[str, Component]) -> Header:
        fields_dict = UniqueKeysDict()
        for child in node:
            if child.tag == 'group':
                child_group = self.parse_message_group(child, dict_fields)
                fields_dict[child_group.name] = child_group
            elif child.tag == 'field':
                child_field = self.parse_message_field(child, dict_fields)
                fields_dict[child_field.name] = child_field
            elif child.tag == 'component':
                child_component  = self.parse_message_component(child, dict_components)
                fields_dict[child_component.name] = child_component
            else:
                raise Exception(f'Malformed XML: unsupported tag "{child.tag}" in the Header definition')
        return Header(fields = fields_dict)

    def get_fields(self) -> Dict[str, Field]:
        fields_dict = UniqueKeysDict()
        for child_field_definition in self.root.findall("fields/field"):
            result_field = self.parse_field(child_field_definition)
            fields_dict[result_field.name] = result_field
        return fields_dict

    def get_components(self, dict_fields: Dict[str, Field]) -> Dict[str, Component]:
        component_dict = UniqueKeysDict()
        for child_component_definition in self.root.findall("components/component"):
            result_component = self.parse_component(child_component_definition, dict_fields)
            component_dict[result_component.name] = result_component
        return component_dict

    def get_messages(self, dict_fields: Dict[str, Field], dict_components: Dict[str, Component]) -> Dict[str, Message]:
        message_dict = UniqueKeysDict()
        for child_message_definition in self.root.findall("messages/message"):
            result_message = self.parse_message(child_message_definition, dict_fields, dict_components)
            message_dict[result_message.name] = result_message
        return message_dict

    def get_header(self, dict_fields: Dict[str, Field], dict_components: Dict[str, Component]) -> Header:
        header = None
        for header_definition in self.root.findall("header"):
            header = self.parse_header(header_definition, dict_fields, dict_components)
        if header == None:
            raise Exception(f'Malformed XML: header is not present')
        return header

    def get_trailer(self, dict_fields: Dict[str, Field], dict_components: Dict[str, Component]) -> Trailer:
        trailer = None
        for trailer_definition in self.root.findall("trailer"):
            trailer = self.parse_trailer(trailer_definition, dict_fields, dict_components)
        if trailer == None:
            raise Exception(f'Malformed XML: trailer is not present')
        return trailer

    #<fix major="4"
    #     minor="4"
    #     copyright="Copyright (C) 2022 Deutsche Boerse AG. All rights reserved."
    #     version="131.430.0.ga-131004030-27">
    #or 
    #
    #    <fix major="4" minor="2">
    def get_schema(self):
        major_version_int = 0
        minor_version_int = 0
        if self.root.tag == "fix":
            major_version_int = attr(self.root, 'major')
            minor_version_int = attr(self.root, 'minor')
            cpyrght_str = attr(self.root, 'copyright', "")
            vrsn_str = attr(self.root, 'version', "")
        else:
            for child_fix_definition in self.root.findall("fix"):
                print("HERE")
                major_version_int = attr(child_fix_definition, 'major')
                minor_version_int = attr(child_fix_definition, 'minor')
                cpyrght_str = attr(child_fix_definition, 'copyright')
                vrsn_str = attr(child_fix_definition, 'version')

        if major_version_int == 0 or minor_version_int == 0:
            raise Exception(f'Malformed XML: major or minor version is not present')

        fields_dict = self.get_fields()
        components_dict = self.get_components(fields_dict)
        message_dict = self.get_messages(fields_dict, components_dict)
        header_def = self.get_header(fields_dict, components_dict)
        trailer_def = self.get_trailer(fields_dict, components_dict)

        return Schema(
            fix_major_version = major_version_int,
            fix_minor_version = minor_version_int,
            copyright = cpyrght_str,
            version = vrsn_str,
            fields = fields_dict,
            components = components_dict,
            message = message_dict,
            header = header_def,
            trailer = trailer_def,
        )

