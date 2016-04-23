from infra.system.core.meta.metaact import MetaAct
from infra.system.resources.specifier import ResourceSpecifier
from infra.system.resources import types
from infra.system.helpers.utils import getScriptDir
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_EXPORTED_API, ARTEFACT_GOLANG_PROJECTS_API_DIFF

INPUT_TYPE_UPSTREAM_SOURCE_CODE = "upstream_source_code"
INPUT_TYPE_USER_DIRECTORY = "user_directory"
import copy

class GoExportedApiDiffAct(MetaAct):

	def __init__(self):
		MetaAct.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__)
		)

		self.reference = {}
		self.compared_with = {}

		self._api_diff = {}

	def _setResource(self, data):
		# upstream source code
		if data["type"] == INPUT_TYPE_UPSTREAM_SOURCE_CODE:
			return ResourceSpecifier().generateUpstreamSourceCode(
				data["project"],
				data["commit"]
			)

		# user directory
		if data["type"] == INPUT_TYPE_USER_DIRECTORY:
			return ResourceSpecifier().generateUserDirectory(
				data["resource"],
				# tarball is implicit, change it to directory
				type = types.RESOURCE_TYPE_DIRECTORY
			)

		raise ValueError("Input type '%s' is not supported:" % data["type"])

	def setData(self, data):
		"""Validation and data pre-processing"""
		if not self._validateInput(data):
			return False

		self.reference = copy.deepcopy(data["reference"])
		self.compared_with = copy.deepcopy(data["compared_with"])

		self.reference["resource"] = self._setResource(self.reference)
		self.compared_with["resource"] = self._setResource(self.compared_with)

		if self.reference["type"] == INPUT_TYPE_USER_DIRECTORY:
			# TODO(jchaloup): update extractor plugin to work without project
			# any project is valid project for user directory
			self.reference["project"] = "."

		if self.compared_with["type"] == INPUT_TYPE_USER_DIRECTORY:
			# TODO(jchaloup): update extractor plugin to work without project
			# any project is valid project for user directory
			self.compared_with["project"] = "."

		return True

	def getData(self):
		"""Validation and data post-processing"""
		return {
			ARTEFACT_GOLANG_PROJECTS_API_DIFF: self._api_diff
		}

	def _getExportedApiArtefact(self, data):
		# if the input is upstream source code, check the storage
		if data["type"] == INPUT_TYPE_UPSTREAM_SOURCE_CODE:
			if self.retrieve_artefacts:
				try:
					return self.ff.bake(self.read_storage_plugin).call({
						"artefact": ARTEFACT_GOLANG_PROJECT_EXPORTED_API,
						"project": data["project"],
						"commit": data["commit"]
					})
				except:
					pass

			artefacts = self.ff.bake("gosymbolsextractor").call(data)
			golang_project_exported_api = self._getArtefactFromData(
				ARTEFACT_GOLANG_PROJECT_EXPORTED_API,
				artefacts
			)

			if self.store_artefacts:
				try:
					self.ff.bake(self.write_storage_plugin).call(golang_project_exported_api)
				except IOError:
					pass

			return golang_project_exported_api

		# user specified directory
		return self._getArtefactFromData(
			ARTEFACT_GOLANG_PROJECT_EXPORTED_API,
			self.ff.bake("gosymbolsextractor").call(data)
		)

	def execute(self):
		"""Implementation of concrete data processor"""
		reference_artefact = self._getExportedApiArtefact(self.reference)
		compared_with_artefact = self._getExportedApiArtefact(self.compared_with)

		# TODO(jchaloup): replace the boolean with exception
		if reference_artefact == {} or compared_with_artefact == {}:
			return False

		# compare apis
		data = {
			"exported_api_1": compared_with_artefact,
			"exported_api_2": reference_artefact
		}

		self._api_diff = self.ff.bake("goapidiff").call(data)

		return True
