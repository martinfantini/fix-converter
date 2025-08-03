from helpers import UniqueKeysDict
import unittest
from definition_helper import *
from schema import *
from definition import *
from helpers import *
from parser import *

class Testing_Definition(unittest.TestCase):

    def test_value_def(self):
        test_value = Field_Value(enum = "TestEnum", description = "TestDescription")
        helper = DefinitionHelper()
        result = helper.get_value_def(test_value)
        self.assertEqual(result.name, "TestEnum")
        self.assertEqual(result.value, "TestEnum")
        self.assertEqual(result.description, "TestDescription")

    def test_field_def_int(self):
        field_value = Field(
            name = "TestName",
            number = 1234,
            field_type = "INT",
            value_by_description = [],
        )
        helper = DefinitionHelper()
        result = helper.get_field_def(field_value)
        self.assertEqual(result.name, "TestName")
        self.assertEqual(result.number, 1234)
        self.assertEqual(result.primitive_type, 'int')
        self.assertEqual(result.is_enum, False)
        
    def test_field_def_enum(self):
        value_desc_dict = UniqueKeysDict()
        value_desc_dict["TestEnum1"] = Field_Value(enum = "TestEnum1", description = "TestEnum1Desc")
        value_desc_dict["TestEnum2"] = Field_Value(enum = "TestEnum2", description = "TestEnum2Desc")
        
        field_value = Field(
            name = "TestName",
            number = 1234,
            field_type = "INT",
            value_by_description = value_desc_dict,
        )
        helper = DefinitionHelper()
        result = helper.get_field_def(field_value)
        self.assertEqual(result.name, "TestName")
        self.assertEqual(result.number, 1234)
        self.assertEqual(result.primitive_type, 'int')
        self.assertEqual(result.is_enum, True)
        self.assertEqual(len(result.values), 2)

    def test_get_group_value_from_message_group(self):
        message_group = MessageGroup(name = "TestGroup", required = False)
        helper = DefinitionHelper()
        result = helper.get_group_value_from_message_group(message_group)
        self.assertEqual(result.name, "TestGroup")
        self.assertEqual(result.required, False)

    def test_get_field_value_from_message_field(self) : 
        message_field = MessageField(name = "TestField", required = True)
        field_dict = UniqueKeysDict()
        field_dict["TestField"] = Field(
            name = "TestField",
            number = 1346,
            field_type = "INT",
            value_by_description = [],
        )
        helper = DefinitionHelper()
        result = helper.get_field_value_from_message_field(message_field, field_dict)
        self.assertEqual(result.name, "TestField")
        self.assertEqual(result.required, True)

    def test_generate_component_definition(self):
        xml_ref = '\
<fix major="4" minor="2">\
  <components>\
    <component name="QuoteReqGrp">\
      <field name="OrderAttributeType" required="N"/>\
      <field name="AllocAccount" required="Y"/>\
      <group name="NoRelatedSym" required="Y">\
        <field name="Symbol"/>\
        <field name="Side" required="Y"/>\
      </group>\
    </component>\
    <component name="DisplayInstruction">\
        <field name="DisplayQty" required="N" />\
        <field name="DisplayMethod" required="Y" />\
    </component>\
    <component name="Instrument">\
        <field name="Symbol" required="Y" />\
        <field name="SecurityID" required="N" />\
        <component name="QuoteReqGrp" required="Y" />\
        <field name="SecurityIDSource" required="N" />\
    </component>\
  </components>\
  <fields>\
    <field number="1084" name="DisplayMethod" type="CHAR">\
        <value enum="1" description="INITIAL"/>\
        <value enum="3" description="RANDOM"/>\
    </field>\
    <field number="22" name="SecurityIDSource" type="STRING">\
        <value enum="M" description="MARKETPLACE_ASSIGNED_IDENTIFIER"/>\
    </field>\
   <field number="1138" name="DisplayQty" type="QTY"/>\
   <field number="48" name="SecurityID" type="STRING"/>\
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
    <field number="146" name="NoRelatedSym" type="NUMINGROUP"/>\
  </fields>\
</fix>\
'
        parser_result = Parser.from_string(xml_ref)
        fields_dict = parser_result.get_fields()
        components_dict = parser_result.get_components(fields_dict)

        helper = DefinitionHelper()
        result = helper.generate_component_definition(components_dict, fields_dict)

        self.assertEqual(len(result), 3)
        component_QuoteReqGrp = result["QuoteReqGrp"]
        self.assertEqual(component_QuoteReqGrp.name, "QuoteReqGrp")
        QuoteReqGrp_OrderAttributeType = component_QuoteReqGrp.fields["OrderAttributeType"]
        self.assertEqual(QuoteReqGrp_OrderAttributeType.name, "OrderAttributeType")
        self.assertEqual(QuoteReqGrp_OrderAttributeType.required , False)

        QuoteReqGrp_NoRelatedSym = component_QuoteReqGrp.fields["NoRelatedSym"]
        self.assertEqual(QuoteReqGrp_NoRelatedSym.name, "NoRelatedSym")
        self.assertEqual(QuoteReqGrp_NoRelatedSym.required , True)
        self.assertEqual(QuoteReqGrp_NoRelatedSym.required_group , False)

        component_DisplayInstruction = result["DisplayInstruction"]
        self.assertEqual(len(component_DisplayInstruction.fields), 2)
        DisplayInstruction_DisplayMethod = component_DisplayInstruction.fields["DisplayMethod"]
        self.assertEqual(DisplayInstruction_DisplayMethod.name, "DisplayMethod")
        self.assertEqual(DisplayInstruction_DisplayMethod.required, True)

        component_Instrument = result["Instrument"]
        self.assertEqual(len(component_Instrument.fields), 6)
        Instrument_NoRelatedSym = component_Instrument.fields["NoRelatedSym"]
        self.assertEqual(Instrument_NoRelatedSym.name, "NoRelatedSym")
        self.assertEqual(Instrument_NoRelatedSym.required , True)
        self.assertEqual(Instrument_NoRelatedSym.required_group , True)

    def test_get_message_definition(self):
        xml_ref = '\
<fix major="4" minor="2">\
    <messages>\
        <message name="EmptyMessage" msgtype="empty"/>\
        <message name="Logon" msgtype="A">\
            <field name="RawDataLength"/>\
            <field name="RawData"/>\
            <field name="EncryptMethod"/>\
            <component name="PartyGrp" required="N"/>\
        </message>\
        <message name="MultilegOrderCancelReplaceRequest" msgtype="AC">\
            <field name="OrderID"/>\
            <field name="OrigClOrdID" required="Y"/>\
            <field name="ClOrdID" required="Y"/>\
            <field name="SecondaryClOrdID"/>\
            <component name="PartyGrp" required="Y"/>\
        </message>\
        <message name="OrderSingle" msgtype="D">\
            <field name="OrderID"/>\
            <group name="NoAllocs" required="Y">\
                <field name="AllocAccount"/>\
            </group>\
        </message>\
    </messages>\
    <components>\
        <component name="PartyGrp">\
            <group name="NoPartyIDs" required="Y">\
                <field name="PartyID"/>\
                <field name="PartyIDSource"/>\
                <field name="PartyRole"/>\
            </group>\
        </component>\
    </components>\
    <fields>\
        <field number="95" name="RawDataLength" type="LENGTH"/>\
        <field number="96" name="RawData" type="DATA"/>\
        <field number="98" name="EncryptMethod" type="INT">\
            <value enum="0" description="NONE"/>\
            <value enum="99" description="CUSTOM"/>\
        </field>\
        <field number="453" name="NoPartyIDs" type="NUMINGROUP" />\
        <field number="448" name="PartyID" type="STRING" />\
        <field number="447" name="PartyIDSource" type="CHAR">\
            <value enum="D" description="PROPRIETARY_CODE"/>\
            <value enum="P" description="SHORT_CODE"/>\
        </field>\
        <field number="452" name="PartyRole" type="INT">\
            <value enum="1" description="EXECUTING_FIRM"/>\
            <value enum="11" description="ORDER_ORIGINATION_TRADER"/>\
            <value enum="12" description="EXECUTING_TRADER" />\
            <value enum="122" description="INVESTMENT_DECISION_MAKER"/>\
            <value enum="3" description="CLIENT_ID"/>\
            <value enum="38" description="POSITION_ACCOUNT"/>\
            <value enum="4" description="CLEARING_FIRM"/>\
            <value enum="44" description="ORDER_ENTRY_OPERATOR_ID"/>\
            <value enum="5" description="INVESTOR_ID" />\
            <value enum="7" description="ENTERING_FIRM" />\
        </field>\
        <field number="37" name="OrderID" type="STRING"/>\
        <field number="41" name="OrigClOrdID" type="STRING"/>\
        <field number="11" name="ClOrdID" type="STRING"/>\
        <field number="526" name="SecondaryClOrdID" type="STRING"/>\
        <field number="78" name="NoAllocs" type="NUMINGROUP"/>\
        <field number="79" name="AllocAccount" type="STRING"/>\
    </fields>\
</fix>\
'

        parser_result = Parser.from_string(xml_ref)
        fields_dict = parser_result.get_fields()
        components_dict = parser_result.get_components(fields_dict)
        messages_dict = parser_result.get_messages(fields_dict, components_dict)

        helper = DefinitionHelper()
        result_component_definition = helper.generate_component_definition(components_dict, fields_dict)
        result_message_definition = helper.generate_message_definition(messages_dict, fields_dict, result_component_definition)

        message_Logon = result_message_definition["Logon"]
        self.assertEqual(message_Logon.msg_type, "A")
        self.assertEqual(len(message_Logon.fields), 4)

        message_MultilegOrderCancelReplaceRequest = result_message_definition["MultilegOrderCancelReplaceRequest"]
        self.assertEqual(message_MultilegOrderCancelReplaceRequest.msg_type, "AC")
        self.assertEqual(len(message_MultilegOrderCancelReplaceRequest.fields), 5)

        message_OrderSingle = result_message_definition["OrderSingle"]
        self.assertEqual(message_OrderSingle.msg_type, "D")
        self.assertEqual(len(message_OrderSingle.fields), 2)
