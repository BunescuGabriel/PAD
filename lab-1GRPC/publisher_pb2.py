# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: publisher.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fpublisher.proto\x12\tGrpcAgent\"2\n\x10PublisherRequest\x12\r\n\x05topic\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\"#\n\x0ePublisherReply\x12\x11\n\tisSuccess\x18\x01 \x01(\x08\x32U\n\tPublisher\x12H\n\x0ePublishMessage\x12\x1b.GrpcAgent.PublisherRequest\x1a\x19.GrpcAgent.PublisherReplyb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'publisher_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_PUBLISHERREQUEST']._serialized_start=30
  _globals['_PUBLISHERREQUEST']._serialized_end=80
  _globals['_PUBLISHERREPLY']._serialized_start=82
  _globals['_PUBLISHERREPLY']._serialized_end=117
  _globals['_PUBLISHER']._serialized_start=119
  _globals['_PUBLISHER']._serialized_end=204
# @@protoc_insertion_point(module_scope)
