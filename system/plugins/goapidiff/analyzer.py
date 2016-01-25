from system.plugins.metaprocessor import MetaProcessor
from system.helpers.artefact_schema_validator import ArtefactSchemaValidator
from system.helpers.schema_validator import SchemaValidator
import logging
from system.helpers.utils import getScriptDir
import time

TYPE_IDENT = "identifier"
TYPE_ARRAY = "array"
TYPE_SLICE = "slice"
TYPE_INTERFACE = "interface"
TYPE_POINTER = "pointer"
TYPE_SELECTOR = "selector"
TYPE_STRUCT = "struct"
TYPE_METHOD = "method"
TYPE_FUNC = "function"
TYPE_ELLIPSIS = "ellipsis"
TYPE_MAP = "map"
TYPE_CHANNEL = "channel"
TYPE_PARENTHESIS = "parenthesis"

class GoApiDiff(MetaProcessor):
	"""
	Input:
	- exported API of a project for a given commit1
	- exported API of a project for a given commit2
	E.g.
	{"exported_api_1": JSON, "exported_api_2": JSON}
	Output:

	Algorithm:
	- both APIs must be of the same project
	"""

	def __init__(self):
		self.exported_api_1 = {}
		self.exported_api_2 = {}
		self.input_validated = False

		# extracted data
		self.new_packages = []
		self.removed_packages = []
		self.diffs = []

	def _validateInput(self, data):
		validator = SchemaValidator("%s/../../artefacts/schemas" % getScriptDir(__file__))
		schema_file = "%s/input_schema.json" % getScriptDir(__file__)
		return validator.validateFromFile(schema_file, data)

	def setData(self, data):
		"""Validation and data pre-processing"""
		logging.info("Validating started: %s" % time.time())
		self.input_validated = True #self._validateInput(data)
		logging.info("Validating done: %s" % time.time())
		if not self.input_validated:
			return false

		self.exported_api_1 = data["exported_api_1"]
		self.exported_api_2 = data["exported_api_2"]

	def getData(self, data):
		"""Validation and data post-processing"""
		if not self.input_validated:
			return {}

		raise NotImplementedError

	def execute(self):
		"""Impementation of concrete data processor"""
		if not self.input_validated:
			return {}

		self._compareApis()

	def _compareApis(self):
		ip1 = []
		ip2 = []

		packages1 = {}
		packages2 = {}

		for pkg in self.exported_api_1["packages"]:
			ip1.append(pkg["package"])
			packages1[pkg["package"]] = pkg

		for pkg in self.exported_api_2["packages"]:
			ip2.append(pkg["package"])
			packages2[pkg["package"]] = pkg

		ip1_set = set(ip1)
		ip2_set = set(ip2)

		self.new_packages = list( ip2_set - ip1_set )
		self.removed_packages = list( ip1_set - ip2_set )
		common_packages = sorted(list( ip1_set & ip2_set ))

		for pkg in common_packages:
			self._comparePackages(packages1[pkg], packages2[pkg])

	def _comparePackages(self, definition1, definition2):
		# compare data types
		if "datatypes" not in definition1:
			logging.error("definition1: datatypes field missing")
			return False

		if "datatypes" not in definition2:
			logging.error("definition2: datatypes field missing")
			return False

		self._compareDataTypes(definition1["datatypes"], definition2["datatypes"])
		#self._compare_func_types(definition1["functions"], definition2["functions"])

	def _compareDataTypes(self, data_types1, data_types2):
		types1_ids = []
		types2_ids = []

		types1 = {}
		types2 = {}

		for datatype in data_types1:
			types1_ids.append(datatype["name"])
			types1[datatype["name"]] = datatype

		for datatype in data_types2:
			types2_ids.append(datatype["name"])
			types2[datatype["name"]] = datatype

		types1_ids_set = set(types1_ids)
		types2_ids_set = set(types2_ids)

		new_type_ids = list(types2_ids_set - types1_ids_set)
		rem_type_ids = list(types1_ids_set - types2_ids_set)
		com_type_ids = list(types1_ids_set & types2_ids_set)

		for datatype in new_type_ids:
			self.diffs.append("+%s type added" % datatype)

		for datatype in rem_type_ids:
			self.diffs.append("-%s type removed" % datatype)

		for type_id in com_type_ids:
			self._compareDataType(types1[type_id]["def"], types2[type_id]["def"])

	def _compareDataType(self, data_type1, data_type2):
		#
		# TODO(jchaloup): add better location of different.
		#  E.g. struct(name):interface:method:struct:int
		#  old in file *** on line ***
		#  new in file *** on line ***
		if data_type1["type"] != data_type2["type"]:
			self.diff.append("-type differs: %s != %s" % (data_type1["type"], data_type2["type"]))
			return
		type = data_type1["type"]

		if type == TYPE_IDENT:
			self._compareIdentifiers(data_type1, data_type2)
			return
		if type == TYPE_STRUCT:
			self._compareStructs(data_type1, data_type2)
			return
		if type == TYPE_INTERFACE:
			self._compareInterfaces(data_type1, data_type2)
			return
		if type == TYPE_FUNC:
			self._compareFunctions(data_type1, data_type2)
			return
		if type == TYPE_SELECTOR:
			self._compareSelectors(data_type1, data_type2)
			return
		if type == TYPE_SLICE:
			self._compareSlices(data_type1, data_type2)
			return
		if type == TYPE_ARRAY:
			self._compareArrays(data_type1, data_type2)
			return
		if type == TYPE_POINTER:
			self._comparePointers(data_type1, data_type2)
			return
		if type == TYPE_CHANNEL:
			self._compareChannels(data_type1, data_type2)
			return
		if type == TYPE_ELLIPSIS:
			self._compareEllipses(data_type1, data_type2)
			return
		if type == TYPE_MAP:
			self._compareMaps(data_type1, data_type2)
			return

		logging.error("%s type not implemented yet" % type)
		return

	def _constructTypeQualifiedName(self, type, full=False):
		"""
		For given type construct its full qualified name.

		AnonymousField = [ "*" ] TypeName .
		TypeName  = identifier | QualifiedIdent .
		QualifiedIdent = PackageName "." identifier .
		"""
		t = type["type"]
		if t == TYPE_IDENT:
			return type["def"]
		elif t == TYPE_POINTER:
			return self._constructTypeQualifiedName(type["def"])
		elif t == TYPE_SELECTOR:
			if full:
				return "%s.%s" % (type["prefix"], type["item"])
			else:
				return type["item"]
		else:
			logging.error("Type %s can not be used for FQN" % t)
			return ""

	def _compareStructs(self, struct1, struct2, name = ""):
		fields1 = []
		fields2 = []

		fields1_types = {}
		fields2_types = {}

		for field in struct1["fields"]:
			if "name" not in field or field["name"] == "":
				name = self._constructTypeQualifiedName(field["def"])
			else:
				name = field["name"]

			fields1.append(name)
			fields1_types[name] = field

		for field in struct2["fields"]:
			if "name" not in field or field["name"] == "":
				name = self._constructTypeQualifiedName(field["def"])
			else:
				name = field["name"]

			fields2.append(name)
			fields2_types[name] = field

		fields1_set = set(fields1)
		fields2_set = set(fields2)

		new_fields = list(fields2_set - fields1_set)
		rem_fields = list(fields1_set - fields2_set)
		com_fields = list(fields1_set & fields2_set)

		for field in new_fields:
			self.diff.append("+struct %s: new field '%s'" % (name, field))

		for field in rem_fields:
			self.diff.append("-struct %s: '%s' field removed" % (name, field))

		for field in com_fields:
			self._compareDataType(fields1_types[field]["def"], fields2_types[field]["def"])

	def _compareIdentifiers(self, ident1, ident2):
		# "identifier": {
		# 	"type": "object",
		# 	"description": "Identifier definition",
		# 	"properties": {
		# 		"type": {
		# 			"type": "string",
		# 			"description": "Type identifier",
		# 			"oneOf": [
		# 				{"enum": ["identifier"]}
		# 			]
		# 		},
		# 		"def": {
		# 			"type": "string",
		# 			"description": "Primitive type or ID",
		# 			"minLength": 1
		# 		}
		# 	},
		# 	"required": ["type", "def"]
		# },
		if ident1["def"] != ident2["def"]:
			self.diffs.append("-identifiers differ in type: %s != %s" % (ident1["def"], ident2["def"]))

	def _compareSelectors(self, selector1, selector2):
		#
		if selector1["item"] != selector2["item"]:
			self.diff.append("-Selector differs in expression: %s != %s" % (selector1["item"], selector2["item"]))

		self._compareDataType(selector1["prefix"], selector2["prefix"])

	def _compareFunctions(self, function1, function2, name = ""):
		# compare params
		l1 = len(function1["params"])
		l2 = len(function2["params"])
		if l1 != l2:
			self.diff.append("-function %s: parameter count changed: %s -> %s" % (name, l1, l2))
			return

		for i in range(0, l1):
			self._compareDataType(function1["params"][i], function2["params"][i])

		# compare results
		l1 = len(function1["results"])
		l2 = len(function2["results"])
		if l1 != l2:
			self.diff.append("-function %s: results count changed: %s -> %s" % (name, l1, l2))
			return

		for i in range(0, l1):
			self._compareDataType(function1["results"][i], function2["results"][i])

	def _compareSlices(self, slice1, slice2):
		self._compareDataType(slice1["elmtype"], slice2["elmtype"])

	def _compareArrays(self, array1, array2):
		self._compareDataType(array1["elmtype"], array2["elmtype"])

	def _comparePointers(self, pointer1, pointer2):
		self._compareDataType(pointer1["def"], pointer2["def"])

	def _compareChannels(self, channel1, channel2):
		if channel1["dir"] != channel2["dir"]:
			self.diff.append("-Channels has different direction: %s -> %s" % (channel1["dir"], channel2["dir"]))

		self._compareDataType(channel1["value"], channel2["value"])

	def _compareEllipses(self, ellipse1, ellipse2):
		self._compareDataType(ellipse1["def"], ellipse2["def"])

	def _compareMaps(self, map1, map2):
		self._compareDataType(map1["keytype"], map2["keytype"])
		self._compareDataType(map1["valuetype"], map2["valuetype"])

	def _compareInterfaces(self, interface1, interface2, name = ""):
		methods1 = []
		methods2 = []

		methods1_types = {}
		methods2_types = {}

		for method in interface1["methods"]:
			methods1.append(method["name"])
			methods1_types[method["name"]] = method["def"]

		for method in interface2["methods"]:
			methods2.append(method["name"])
			methods2_types[method["name"]] = method["def"]

		methods1_set = set(methods1)
		methods2_set = set(methods2)

		new_methods = list(methods2_set - methods1_set)
		rem_methods = list(methods1_set - methods2_set)
		com_methods = list(methods1_set & methods2_set)

		for method in new_methods:
			self.diffs.append("+interface %s: new method: %s" % (name, method))
		for method in rem_methods:
			self.diffs.append("-interface %s: %s method removed" % (name, method))

		for method in com_methods:
			self._compareDataType(methods1_types[method], methods2_types[method])

	def _compare_func_types(self, func_types1, func_types2):
		func1_ids = []
		func2_ids = []

		for functype in func_types1:
			func1_ids.append(functype["name"])

		for functype in func_types2:
			func2_ids.append(functype["name"])

		func1_ids_set = set(func1_ids)
		func2_ids_set = set(func2_ids)

		new_func_ids = list(func2_ids_set - func1_ids_set)
		rem_func_ids = list(func1_ids_set - func2_ids_set)
		com_func_ids = list(func1_ids_set & func2_ids_set)

		#print new_func_ids
		#print rem_func_ids
		#print com_func_ids
