# Copyright (C) 2025 Roberto Martin Fantini <martin.fantini@gmail.com>
# This file may be distributed under the terms of the GNU GPLv3 license

import unittest
from app.parser import *
from app.schema import *

class Testing_Parser(unittest.TestCase):

    def test_ParseFieldDefinition(self):

        xml_ref = '\
<?xml version="1.0" encoding="UTF-8"?>\
<fix major="4" minor="2">\
    <fields>\
        <field number="9701" name="OmnibusAccount" type="STRING"/>\
        <field number="9706" name="FeeBilling" type="CHAR">\
            <value enum="B" description="CBOE_MEMBER"/>\
            <value enum="C" description="CUSTOMER"/>\
            <value enum="E" description="EQUITY_MEMBER"/>\
            <value enum="H" description="FIRM"/>\
            <value enum="L" description="LESSEE"/>\
       </field>\
    </fields>\
</fix>\
'
        parser_result = Parser.from_string(xml_ref)
        field_types_dict = parser_result.get_fields()

        field_FeeBilling = field_types_dict["FeeBilling"]
        self.assertEqual(field_FeeBilling.name, "FeeBilling")
        self.assertEqual(field_FeeBilling.number, 9706)
        self.assertEqual(field_FeeBilling.field_type, "CHAR")
        self.assertEqual(len(field_FeeBilling.value_by_description), 5)

        customer_value = field_FeeBilling.value_by_description["CUSTOMER"]
        self.assertEqual(customer_value.enum, "C")
        self.assertEqual(customer_value.description, "CUSTOMER")

        field_OmnibusAccount = field_types_dict["OmnibusAccount"]
        self.assertEqual(field_OmnibusAccount.name, "OmnibusAccount")
        self.assertEqual(field_OmnibusAccount.number, 9701)
        self.assertEqual(field_OmnibusAccount.field_type, "STRING")
        self.assertEqual(len(field_OmnibusAccount.value_by_description), 0)

    def test_TestComponents(self):

        xml_ref = '\
<fix major="4" minor="2">\
  <components>\
    <component name="QuoteReqGrp">\
      <field name="OrderAttributeType" required="N"/>\
      <field name="AllocAccount" required="Y"/>\
      <group name="NoRelatedSym">\
        <field name="Symbol"/>\
        <field name="Side" required="Y"/>\
      </group>\
    </component>\
  </components>\
  <fields>\
   <field number="2594" name="OrderAttributeType" type="INT">\
       <value enum="0" description="AGGREGATED_ORDER"/>\
       <value enum="1" description="PENDING_ALLOCATION"/>\
       <value enum="2" description="LIQUIDITY_PROVISION_ACTIVITY_ORDER"/>\
       <value enum="3" description="RISK_REDUCTION_ORDER"/>\
       <value enum="4" description="ALGORITHMIC_ORDER"/>\
       <value enum="5" description="SYSTEMATIC_INTERNALIZER_ORDER"/>\
   </field>\
    <field number="55" name="Symbol" type="STRING"/>\
    <field number="38" name="OrderQty" type="FLOAT"/>\
    <field number="54" name="Side" type="CHAR">\
      <value enum="1" description="BUY"/>\
      <value enum="2" description="SELL"/>\
      <value enum="8" description="CROSS"/>\
      <value enum="B" description="AS_DEFINED"/>\
      <value enum="C" description="OPPOSITE"/>\
    </field>\
    <field number="79" name="AllocAccount" type="STRING"/>\
  </fields>\
</fix>\
'
        parser_result = Parser.from_string(xml_ref)
        field_types_dict = parser_result.get_fields()

        components_type_dict = parser_result.get_components(field_types_dict)
        component_QuoteReqGrp = components_type_dict["QuoteReqGrp"]
        self.assertEqual(component_QuoteReqGrp.name, "QuoteReqGrp")

        component_OrderAttributeType = component_QuoteReqGrp.field_group_by_name["OrderAttributeType"]
        self.assertEqual(component_OrderAttributeType.name, "OrderAttributeType")
        self.assertEqual(component_OrderAttributeType.required, False)

        component_AllocAccount = component_QuoteReqGrp.field_group_by_name["AllocAccount"]
        self.assertEqual(component_AllocAccount.name, "AllocAccount")
        self.assertEqual(component_AllocAccount.required, True)
        
        component_NoRelatedSym = component_QuoteReqGrp.field_group_by_name["NoRelatedSym"]
        self.assertEqual(component_NoRelatedSym.name, "NoRelatedSym")
        self.assertEqual(component_NoRelatedSym.required, False)

        component_NoRelatedSym_Symbol = component_NoRelatedSym.field_by_name["Symbol"]
        self.assertEqual(component_NoRelatedSym_Symbol.name, "Symbol")
        self.assertEqual(component_NoRelatedSym_Symbol.required, False)

        component_NoRelatedSym_Side = component_NoRelatedSym.field_by_name["Side"]
        self.assertEqual(component_NoRelatedSym_Side.name, "Side")
        self.assertEqual(component_NoRelatedSym_Side.required, True)

    def test_TestMessages(self):

        xml_ref = '\
<fix major="4" minor="2">\
  <messages>\
    <message name="Heartbeat" msgtype="0">\
      <field name="TestReqID"/>\
      <field name="ClOrdID" required="Y"/>\
    </message>\
    <message name="TestRequest" msgtype="1">\
      <field name="TestReqID" required="Y"/>\
      <component name="InstrmtLegGrp" required="Y"/>\
    </message>\
  </messages>\
  <components>\
    <component name="InstrmtLegGrp">\
        <field name="Side" required="Y"/>\
    </component>\
  </components>\
  <fields>\
    <field number="11" name="ClOrdID" type="STRING"/>\
    <field number="54" name="Side" type="CHAR">\
      <value enum="1" description="BUY"/>\
      <value enum="2" description="SELL"/>\
      <value enum="8" description="CROSS"/>\
      <value enum="B" description="AS_DEFINED"/>\
      <value enum="C" description="OPPOSITE"/>\
    </field>\
    <field number="112" name="TestReqID" type="STRING"/>\
  </fields>\
</fix>\
'

        parser_result = Parser.from_string(xml_ref)
        field_types_dict = parser_result.get_fields()

        component_types_dict = parser_result.get_components(field_types_dict)

        messages_type_dict = parser_result.get_messages(field_types_dict, component_types_dict)

        messages_Heartbeat = messages_type_dict["Heartbeat"]
        self.assertEqual(messages_Heartbeat.msg_type, "0")

        messages_Heartbeat_TestReqID = messages_Heartbeat.fields["TestReqID"]
        self.assertEqual(messages_Heartbeat_TestReqID.name, "TestReqID")
        self.assertEqual(messages_Heartbeat_TestReqID.required, False)

        messages_Heartbeat_ClOrdID = messages_Heartbeat.fields["ClOrdID"]
        self.assertEqual(messages_Heartbeat_ClOrdID.name, "ClOrdID")
        self.assertEqual(messages_Heartbeat_ClOrdID.required, True)

        messages_TestRequest = messages_type_dict["TestRequest"]
        self.assertEqual(messages_TestRequest.msg_type, "1")

        messages_TestRequest_TestReqID = messages_TestRequest.fields["TestReqID"]
        self.assertEqual(messages_TestRequest_TestReqID.name, "TestReqID")
        self.assertEqual(messages_TestRequest_TestReqID.required, True)

        messages_TestRequest_InstrmtLegGrp = messages_TestRequest.fields["InstrmtLegGrp"]
        self.assertEqual(messages_TestRequest_InstrmtLegGrp.name, "InstrmtLegGrp")
        self.assertEqual(messages_TestRequest_InstrmtLegGrp.required, True)

    def test_TestHeader(self):
        xml_ref = '\
<fix major="4" minor="2">\
  <header>\
    <field name="BeginString"/>\
  </header>\
  <fields>\
    <field number="10" name="BeginString" type="INT"/>\
  </fields>\
</fix>\
'
        parser_result = Parser.from_string(xml_ref)
        field_types_dict = parser_result.get_fields()

        header_result = parser_result.get_header(field_types_dict, None)
        self.assertEqual(len(header_result.fields), 1)

    def test_TestTrailer(self):
        xml_ref = '\
<fix major="4" minor="2">\
  <trailer>\
    <field name="CheckSum" required="Y"/>\
  </trailer>\
  <fields>\
    <field number="10" name="CheckSum" type="INT"/>\
  </fields>\
</fix>\
'
        parser_result = Parser.from_string(xml_ref)
        field_types_dict = parser_result.get_fields()

        trailer_result = parser_result.get_trailer(field_types_dict, None)
        self.assertEqual(len(trailer_result.fields), 1)

    def test_TestSchema(self):
        parser_result = Parser.from_file("resources/fix_definition.xml")
        schema_result = parser_result.get_schema(None)

        self.assertEqual(len(schema_result.header.fields), 18)
        self.assertEqual(len(schema_result.trailer.fields), 1)

    def test_TestSchemaCash(self):
        parser_result = Parser.from_file("resources/FIXLF44_Cash.xml")
        schema_result = parser_result.get_schema(None)

        self.assertEqual(len(schema_result.header.fields), 10)
        self.assertEqual(len(schema_result.trailer.fields), 1)
