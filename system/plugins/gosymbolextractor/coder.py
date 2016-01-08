"""
## Predefined types
predifined types:
	bool byte complex64 complex128 error float32 float64
	int int8 int16 int32 int64 rune string
	uint uint8 uint16 uint32 uint64 uintptr

No change
## Types

### Ident type

{u'type': u'ident', u'def': u'dynamicTable'}

### Array types

ArrayType   = "[" ArrayLength "]" ElementType .

The length is part of the array's type;
it must evaluate to a non-negative constant representable by a value of type int.
string: [INT] TYPE

### Slice types

SliceType = "[" "]" ElementType .

### Structs

StructType     = "struct" "{" { FieldDecl ";" } "}" .
FieldDecl      = (IdentifierList Type | AnonymousField) [ Tag ] .
AnonymousField = [ "*" ] TypeName .
Tag            = string_lit .


## structs
type ID struct {
        [ID    TYPE]+
}

into

"struct ID {ID TYPE[,ID TYPE]*}"

"""

import logging

PREDEFINED_TYPES = ["bool", "byte", "complex64", "complex128", "error", "float32", "float64", "int", "int8", "int16", "int32", "int64", "rune", "string", "uint", "uint8", "uint16", "uint32", "uint64", "uintptr"]

TYPE_IDENT = "ident"
TYPE_ARRAY = "array"
TYPE_SLICE = "slice"
TYPE_INTERFACE = "interface"
TYPE_POINTER = "pointer"
TYPE_SELECTOR = "selector"
TYPE_STRUCT = "struct"
TYPE_METHOD = "method"
TYPE_FUNC = "func"
TYPE_ELLIPSIS = "ellipsis"
TYPE_MAP = "map"
TYPE_CHANNEL = "channel"
TYPE_PARENTHESIS = "parenthesis"

class GoTypeCoder:
	"""
	Serialization of tree-like data types representation
	"""

	def _is_predefined_type(self, type):
		if type in PREDEFINED_TYPES:
			return True
		return False

	def _predefined_type_to_string(self, type):
		return type

	def _is_ident(self, type):
		if type["type"] == TYPE_IDENT:
			return True
		return False

	def _ident_to_string(self, type):
		#
		#
		#
		return "%s {%s}" % (TYPE_IDENT, type["def"])

	def _is_array(self, type):
		if type["type"] == TYPE_ARRAY:
			return True
		return False

	def _array_to_string(self, type):
		# ArrayType   = "[" ArrayLength "]" ElementType .
		# 
		# [INT] TYPE
		return ""

	def _is_struct(self, type):
		if type["type"] == TYPE_STRUCT:
			return True
		return False

	def _struct_to_string(self, type):
		#
		#
		# struct {}
		fields = []
		for field in type["def"]:
			field_type_str = self._type_to_string(field["def"])
			fields.append("'%s' %s" % (field["name"], field_type_str))

		return "%s %s {%s}" % (TYPE_STRUCT, type["name"], ", ".join(fields))

	def _type_to_string(self, type):
		if self._is_struct(type):
			return self._struct_to_string(type)
		if self._is_ident(type):
			return self._ident_to_string(type)

		logging.error("%s type not implemented" % type["type"])

		return ""

	def __init__(self, type):
		self.type = type

	def code(self):
		return self._type_to_string(self.type)
