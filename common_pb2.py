# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: common.proto
# Protobuf Python Version: 6.31.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    0,
    '',
    'common.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0c\x63ommon.proto\"5\n\tFileChunk\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\x0c\x12\x17\n\x04type\x18\x02 \x01(\x0e\x32\t.FileType\"A\n\x10ProgressResponse\x12\x11\n\x07percent\x18\x01 \x01(\x02H\x00\x12\x10\n\x06result\x18\x02 \x01(\tH\x00\x42\x08\n\x06update\"\x18\n\x08\x46ileSize\x12\x0c\n\x04size\x18\x01 \x01(\x05*\x1e\n\x08\x46ileType\x12\x07\n\x03PDF\x10\x00\x12\t\n\x05IMAGE\x10\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'common_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_FILETYPE']._serialized_start=164
  _globals['_FILETYPE']._serialized_end=194
  _globals['_FILECHUNK']._serialized_start=16
  _globals['_FILECHUNK']._serialized_end=69
  _globals['_PROGRESSRESPONSE']._serialized_start=71
  _globals['_PROGRESSRESPONSE']._serialized_end=136
  _globals['_FILESIZE']._serialized_start=138
  _globals['_FILESIZE']._serialized_end=162
# @@protoc_insertion_point(module_scope)
