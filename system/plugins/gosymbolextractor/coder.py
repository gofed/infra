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
		print type
		if "name" in type:
			return "%s '%s' {%s}" % (TYPE_IDENT, type["name"], type["def"]["def"])
		else:
			return "%s {%s}" % (TYPE_IDENT, type["def"])

	def _is_array(self, type):
		if type["type"] == TYPE_ARRAY:
			return True
		return False

	def _array_to_string(self, type):
		# ArrayType   = "[" ArrayLength "]" ElementType .
		# {u'elmtype': {u'type': u'ident', u'def': u'byte'}, u'type': u'array', u'name': u''}
		# [INT] TYPE
		elmtype_to_string = self._type_to_string(type["elmtype"])
		return "%s %s {%s}" % (TYPE_ARRAY, type["name"], elmtype_to_string)

	def _is_slice(self, type):
		if type["type"] == TYPE_SLICE:
			return True
		return False

	def _slice_to_string(self, type):
		# SliceType = "[" "]" ElementType .
		#
		# slice {TYPE}
		element_type_to_string = self._type_to_string(type["elmtype"])
		return "%s {%s}" % (TYPE_SLICE, element_type_to_string)

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

		return "%s '%s' {%s}" % (TYPE_STRUCT, type["name"], ", ".join(fields))

	def _is_selector(self, type):
		if type["type"] == TYPE_SELECTOR:
			return True
		return False

	def _selector_to_string(self, type):
		# {u'item': u'Writer', u'prefix': {u'type': u'ident', u'def': u'io'}, u'type': u'selector'}
		#
		# selector ITEM {PREFIX}
		prefix_type_string = self._type_to_string(type["prefix"])
		return "%s %s {%s}" % (TYPE_SELECTOR, type["item"], prefix_type_string)

	def _is_function_type(self, type):
		if type["type"] == TYPE_FUNC:
			return True
		return False

	def _function_to_string(self, type):
		# {u'name': u'emit', u'def': {u'params': [{u'type': u'ident', u'def': u'HeaderField'}], u'type': u'func', u'results': []}
		#
		# func NAME {TYPE[,TYPE]*} {TYPE[,TYPE]*}
		args = []
		for param in type["params"]:
			args.append(self._type_to_string(param))
		fnc_args_to_string = ", ".join(args)

		res = []
		for param in type["results"]:
			res.append(self._type_to_string(param))
		fnc_res_to_string = ", ".join(res)

		if "name" not in type:
			return "%s {%s} {%s}" % (TYPE_FUNC, fnc_args_to_string, fnc_res_to_string)
		else:
			return "%s %s {%s} {%s}" % (TYPE_FUNC, type["name"], fnc_args_to_string, fnc_res_to_string)

	def _is_map(self, type):
		if type["type"] == TYPE_MAP:
			return True
		return False

	def _map_to_string(self, type):
		# {u'type': u'map', u'name': u'', u'def': {u'keytype': {u'type': u'ident', u'def': u'string'}, u'valuetype': {u'elmtype': {u'type': u'pointer', u'def': {u'type': u'ident', u'def': u'clientConn'}}, u'type': u'slice', u'name': u''}}}
		# map NAME {KEYTYPE} {VALUETYPE}
		keytype_to_string = self._type_to_string(type["def"]["keytype"])
		valuetype_to_string = self._type_to_string(type["def"]["valuetype"])
		return "%s %s {%s} {%s}" % (TYPE_MAP, type["name"], keytype_to_string, valuetype_to_string)

	def _is_pointer(self, type):
		if type["type"] == TYPE_POINTER:
			return True
		return False

	def _pointer_to_string(self, type):
		# {u'type': u'pointer', u'def': {u'type': u'ident', u'def': u'clientConn'}}
		#
		# pointer {TYPE}
		pointer_type_to_string = self._type_to_string(type["def"])
		return "%s {%s}" % (TYPE_POINTER, pointer_type_to_string)

	def _is_method(self, type):
		if type["type"] == TYPE_METHOD:
			return True
		return False

	def _method_to_string(self, type):
		# {u'type': u'method', u'name': u'Header', u'def': {u'params': [], u'type': u'func', u'results': [{u'type': u'ident', u'def': u'FrameHeader'}]}}
		# method NAME {TYPE[,TYPE]*} {TYPE[,TYPE]*}
		params_as_strings = []
		for param in type["def"]["params"]:
			params_as_strings.append(self._type_to_string(param))

		results_as_strings = []
		for result in type["def"]["results"]:
			results_as_strings.append(self._type_to_string(result))

		return "%s %s {%s} {%s}" % (TYPE_METHOD, type["name"], ", ".join(params_as_strings), ", ".join(results_as_strings) )

	def _is_interface(self, type):
		if type["type"] == TYPE_INTERFACE:
			return True
		return False

	def _interface_to_string(self, type):
		# {u'type': u'interface', u'name': u'Frame', u'def': [{u'type': u'method', u'name': u'Header', u'def': {u'params': [], u'type': u'func', u'results': [{u'type': u'ident', u'def': u'FrameHeader'}]}}, {u'type': u'method', u'name': u'invalidate', u'def': {u'type': u'func', u'params': [], u'results': []}}]}
		#
		# interface {FNC[,FNC]*} or just interface{}
		fncs = []
		for fnc in type["def"]:
			fncs.append( self._method_to_string(fnc) )

		return "%s {%s}" % (TYPE_INTERFACE, ", ".join(fncs))

	def _type_to_string(self, type):
		if self._is_struct(type):
			return self._struct_to_string(type)
		if self._is_ident(type):
			return self._ident_to_string(type)
		if self._is_selector(type):
			return self._selector_to_string(type)
		if self._is_slice(type):
			return self._slice_to_string(type)
		if self._is_function_type(type):
			return self._function_to_string(type)
		if self._is_array(type):
			return self._array_to_string(type)
		if self._is_map(type):
			return self._map_to_string(type)
		if self._is_pointer(type):
			return self._pointer_to_string(type)
		if self._is_interface(type):
			return self._interface_to_string(type)

		logging.error("%s type not implemented" % type["type"])
		logging.error(type)

		return ""

	def __init__(self, type):
		self.type = type

	def code(self):
		return self._type_to_string(self.type)
