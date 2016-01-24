from system.plugins.metaprocessor import MetaProcessor
from system.helpers.artefact_schema_validator import ArtefactSchemaValidator
from system.helpers.schema_validator import SchemaValidator
import logging
from system.helpers.utils import getScriptDir

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

	def _validate_input(self, data):
		validator = SchemaValidator("%s/../../artefacts/schemas" % getScriptDir(__file__))
		schema_file = "%s/input_schema.json" % getScriptDir(__file__)
		return validator.validateFromFile(schema_file, data)

	def setData(self, data):
		"""Validation and data pre-processing"""
		self.input_validated = self._validate_input(data)
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

		self._compage_apis()

	def _compage_apis(self):
		ip1 = []
		ip2 = []
		for pkg in self.exported_api_1["packages"]:
			ip1.append(pkg["package"])

		for pkg in self.exported_api_2["packages"]:
			ip2.append(pkg["package"])

		print ip1
		print ip2



