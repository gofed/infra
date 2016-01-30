from system.acts.metaact import MetaAct
from system.resources.specifier import ResourceSpecifier
from system.resources import types
from system.core.functionfactory import FunctionFactory
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES

import json

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
		self.golang_project_packages = {}

	def _validateData(self, data):
		return True

	def setData(self, data):
		"""Validation and data pre-processing"""
		# TODO(jchaloup): specify JSON Schema for input
		self._validateData(data)
		self.data = data

	def getData(self):
		"""Validation and data post-processing"""
		# TODO(jchaloup): specify JSON Schema for output
		return self.golang_project_packages

	def execute(self):
		"""Impementation of concrete data processor"""
		res_spec = ResourceSpecifier()
		dir_res  = res_spec.generateUserDirectory(self.data["source_code_directory"], type = types.RESOURCE_TYPE_DIRECTORY)
		# retrieve resource
		self.data["source_code_directory"] = dir_res

		# extract data from resource
		data = self.ff.bake("gosymbolsextractor").call(self.data)
		# get ARTEFACT_GOLANG_PROJECT_PACKAGES artefact
		self.golang_project_packages = {}
		for item in data:
			if item["artefact"] == ARTEFACT_GOLANG_PROJECT_PACKAGES:
				self.golang_project_packages = item
				break
