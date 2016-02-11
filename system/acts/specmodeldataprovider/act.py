from system.core.meta.metaact import MetaAct
from system.resources.specifier import ResourceSpecifier
from system.resources import types
from system.core.functions.functionfactory import FunctionFactory
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES
from system.core.functions.types import FunctionNotFoundError, FunctionFailedError
from system.helpers.schema_validator import SchemaValidator
from system.helpers.utils import getScriptDir

import json

INPUT_TYPE_UPSTREAM_SOURCE_CODE = 1
INPUT_TYPE_USER_DIRECTORY = 2

class SpecModelDataProviderAct(MetaAct):
	"""
	Input:
	- source_code_directory
	- ipprefix
	Output:
	- data to be thought to be usefull for spec file generator
	"""
	def __init__(self):
		self.ff = FunctionFactory()

		# flags
		self.input_validated = False
		self.input_type = ""

		# extracted data
		self.golang_project_packages = {}

	def _validateInput(self, data):
		validator = SchemaValidator()
		schema = "%s/input_schema.json" % getScriptDir(__file__)
		self.input_validated = validator.validateFromFile(schema, data)
		return self.input_validated

	def setData(self, data):
		"""Validation and data pre-processing"""
		if not self._validateInput(data):
			return False

		self.data = data

		# specify resource
		# upstream source code
		if "project" in data and "commit" in data:
			self.input_type = INPUT_TYPE_UPSTREAM_SOURCE_CODE
			self.data["resource"] = ResourceSpecifier().generateUpstreamSourceCode(data["project"], data["commit"])
			return True
		# user directory
		if "resource" in data:
			self.input_type = INPUT_TYPE_USER_DIRECTORY
			self.data["resource"] = ResourceSpecifier().generateUserDirectory(data["resource"], type = types.RESOURCE_TYPE_DIRECTORY)
			return True

		return False

	def getData(self):
		"""Validation and data post-processing"""
		# TODO(jchaloup): specify JSON Schema for output
		return self.golang_project_packages

	def execute(self):
		"""Impementation of concrete data processor"""
		try:
			if self.input_type == INPUT_TYPE_UPSTREAM_SOURCE_CODE:
				ok, self.golang_project_packages = self.ff.bake("etcdstoragereader").call({
					"artefact": ARTEFACT_GOLANG_PROJECT_PACKAGES,
					"project": self.data["project"],
					"commit": self.data["commit"]
				})
				if not ok:
					data = self.ff.bake("gosymbolsextractor").call(self.data)
					self.golang_project_packages = data[0]
					# store the data
					# TODO(jchaloup): check it was actually successful
					# TODO(jchaloup): this is for testing only, remove after switching to production
					self.ff.bake("etcdstoragewriter").call(self.golang_project_packages)
			else:
				# extract data from resource
				data = self.ff.bake("gosymbolsextractor").call(self.data)
				for item in data:
					if item["artefact"] == ARTEFACT_GOLANG_PROJECT_PACKAGES:
						self.golang_project_packages = item
					break

				# TODO(jchaloup): check self.golang_project_packages != {}

		except FunctionNotFoundError as e:
			print "spec-model-data-provider-act: %s" % e
			return False
		except FunctionFailedError as e:
			print "spec-model-data-provider-act: %s" % e
			return False
		except types.ResourceNotFoundError as e:
			print "spec-model-data-provider-act: %s" % e
			return False

		return True
