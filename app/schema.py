# Copyright (C) 2025 R. Martin Fantini <martin.fantini@gmail.com>
# This file may be distributed under the terms of the GNU GPLv3 license

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Union

#   <field number="9706" name="FeeBilling" type="CHAR">
#      <value enum="B" description="CBOE_MEMBER"/>
#      <value enum="C" description="CUSTOMER"/>
#      <value enum="E" description="EQUITY_MEMBER"/>
#      <value enum="H" description="FIRM"/>
#      <value enum="L" description="LESSEE"/>
#   </field>
@dataclass(frozen=True)
class Field:
    name: str = field(default_factory=str)
    number: Optional[int] = field(default=None)
    field_type: str = field(default_factory=str)
    value_by_description: Dict[str, Field_Value] = field(default_factory=dict)

# <value enum="L" description="LESSEE"/>
@dataclass(frozen=True)
class Field_Value:
    enum: str = field(default_factory=str)
    description: str = field(default_factory=str)

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
@dataclass(frozen=True)
class Component:
    name: str = field(default_factory=str)
    field_group_by_name: Dict[str, Union[MessageField, MessageComponent, MessageGroup]] = field(default_factory=dict)

#   <group name="NoQuoteEntries">
#      <field name="Symbol"/>
#      <field name="SecurityDesc"/>
#   </group>
# or
#   <group name="NoRiskLimitTypes" required="Y">
#       <field name="RiskLimitType" required="Y" />
#   </group>
@dataclass(frozen=True)
class MessageGroup:
    name: str = field(default_factory=str)
    required: bool = field(default=False)
    field_by_name: Dict[str, Union[MessageField, MessageComponent, MessageGroup]] = field(default_factory=dict)

#    <field name="CheckSum" required="Y"/>
@dataclass(frozen=True)
class MessageField:
    name: str = field(default_factory=str)
    required: Optional[bool] = field(default=False)

# <component name="Parties" required="Y" />
@dataclass(frozen=True)
class MessageComponent:
    name: str = field(default_factory=str)
    required: Optional[bool] = field(default=False)

#        <message name="UserPartyRiskLimitsRequest" msgtype="UCL" msgcat="app">
#        	<component name="Parties" required="Y" />
#        	<field name="MarketSegmentID" required="Y" />
#        	<field name="RiskLimitRequestID" required="Y" />
#        	<field name="RiskLimitGroup" required="N" />
#        </message>
# or
#        <message name="OrderCancelReplaceRequest" msgtype="G">
@dataclass(frozen=True)
class Message:
    name: str = field(default_factory=str)
    msg_type: str = field(default_factory=str)
    msg_category: Optional[str] = field(default=None)
    fields: Dict[str, Union[MessageField, MessageComponent, MessageGroup]] = field(default_factory=dict)

#  <trailer>
#    <field name="CheckSum" required="Y"/>
#  </trailer>
@dataclass(frozen=True)
class Trailer:
    fields: Dict[str, Union[MessageField, MessageComponent, MessageGroup]] = field(default_factory=dict)

#    <header>
#    	<field name="BeginString" required="Y" />
#    	<field name="BodyLength" required="Y" />
#    	<field name="MsgType" required="Y" />
#    	<field name="MsgSeqNum" required="Y" />
#    	<field name="PossDupFlag" required="N" />
#    	<field name="SenderCompID" required="Y" />
#    	<field name="SendingTime" required="Y" />
#    	<field name="TargetCompID" required="Y" />
#    	<field name="PossResend" required="N" />
#    	<field name="OrigSendingTime" required="N" />
#    </header>
#    or 
#  <header>
#    <field name="BeginString"/>
#    <field name="BodyLength"/>
#    <field name="MsgType" required="Y"/>
#    <field name="SenderCompID"/>
#    <field name="TargetCompID"/>
#    <field name="MsgSeqNum" required="Y"/>
#    <field name="LastMsgSeqNumProcessed"/>
#    <field name="PossDupFlag"/>
#    <field name="SenderSubID"/>
#    <field name="SendingTime"/>
#    <field name="TargetSubID"/>
#    <field name="PossResend"/>
#    <field name="OrigSendingTime"/>
#    <field name="SenderLocationID"/>
#    <field name="TargetLocationID"/>
#    <field name="OnBehalfOfCompID"/>
#    <field name="OnBehalfOfSubID"/>
#    <field name="DeliverToCompID"/>
#  </header>
@dataclass(frozen=True)
class Header:
    fields: Dict[str, Union[MessageField, MessageComponent, MessageGroup]] = field(default_factory=dict)

#<fix major="4"
#     minor="4"
#     copyright="Copyright (C) 2022 Deutsche Boerse AG. All rights reserved."
#     version="131.430.0.ga-131004030-27">
#or 
#
#    <fix major="4" minor="2">
@dataclass(frozen=True)
class Schema:
    fix_minor_version: int = field(default=0)
    fix_major_version: int = field(default=0)
    copyright: Optional[str] = field(default=None)
    package: Optional[str] = field(default=None)
    version: Optional[str] = field(default=None)
    fields: Dict[str, Field] = field(default_factory=dict)
    components: Dict[str, Component] = field(default_factory=dict)
    message: Dict[str, Message] = field(default_factory=dict)
    header: Header = field(default=None)
    trailer: Trailer = field(default=None)
