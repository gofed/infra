from infra.system.core.meta.metaact import MetaAct
from infra.system.resources.specifier import ResourceSpecifier
from infra.system.resources import types
from infra.system.core.acts import types as acttypes
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES, ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA
from infra.system.core.functions.types import FunctionNotFoundError, FunctionFailedError
from infra.system.helpers.schema_validator import SchemaValidator
from infra.system.helpers.utils import getScriptDir
from gofed_lib.go.data2specmodeldata import Data2SpecModelData

import json
import copy

INPUT_TYPE_UPSTREAM_SOURCE_CODE = "upstream_source_code"
INPUT_TYPE_USER_DIRECTORY = "user_directory"

class SpecModelDataProviderAct(MetaAct):
	"""
	Input:
	- source_code_directory
	- ipprefix
	Output:
	- data to be thought to be usefull for spec file generator
	"""
	def __init__(self):
		MetaAct.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__)
		)

		# extracted data
		self.golang_project_packages = {}
		self.golang_project_content_metadata = {}

	def setData(self, data):
		"""Validation and data pre-processing"""
		if not self._validateInput(data):
			return False

		self.data = copy.deepcopy(data)

		# upstream source code
		if data["type"] == INPUT_TYPE_UPSTREAM_SOURCE_CODE:
			self.data["resource"] = ResourceSpecifier().generateUpstreamSourceCode(
				data["project"],
				data["commit"]
			)
			return True

		# user directory
		if data["type"] == INPUT_TYPE_USER_DIRECTORY:
			self.data["resource"] = ResourceSpecifier().generateUserDirectory(
				data["resource"],
				# tarball is implicit, change it to directory
				type = types.RESOURCE_TYPE_DIRECTORY
			)
			return True

		return False

	def getData(self):
		"""Validation and data post-processing"""
		return {
			ARTEFACT_GOLANG_PROJECT_PACKAGES: self.golang_project_packages,
			ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA: self.golang_project_content_metadata
		}

	def _readPackagesData(self, project, commit):
		return self.ff.bake(self.read_storage_plugin).call({
			"artefact": ARTEFACT_GOLANG_PROJECT_PACKAGES,
			"project": project,
			"commit": commit
		})

	def _readContentData(self, project, commit):
		return self.ff.bake(self.read_storage_plugin).call({
			"artefact": ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA,
			"project": project,
			"commit": commit
		})

	def _extractPackagesData(self, store = False):
		artefacts = self.ff.bake("gosymbolsextractor").call(self.data)
		self.golang_project_packages = self._getArtefactFromData(
			ARTEFACT_GOLANG_PROJECT_PACKAGES,
			artefacts
		)

		if not store:
			return

		if not self.store_artefacts:
			return

		try:
			data = self.ff.bake(self.write_storage_plugin).call(self.golang_project_packages)
		except IOError as e:
			logging.error(e)
			# Just log the data could not be stored

	def _extractContentData(self, input_data, store = False):
		self.golang_project_content_metadata = self.ff.bake("goprojectcontentmetadataextractor").call(input_data)

		if not store:
			return

		if not self.store_artefacts:
			return

		try:
			data = self.ff.bake(self.write_storage_plugin).call(self.golang_project_content_metadata)
		except IOError as e:
			logging.error(e)
			# Just log the data could not be stored

	def execute(self):
		"""Impementation of concrete data processor"""
		if self.retrieve_artefacts and self.data["type"] == INPUT_TYPE_UPSTREAM_SOURCE_CODE:
			# Get golang-project-packages artefact
			try:
				self.golang_project_packages = self._readPackagesData(
					self.data["project"],
					self.data["commit"]
				)
			except KeyError as e:
				self._extractPackagesData(True)

			# Get golang-project-content-metadata
			try:
				self.golang_project_content_metadata = self._readContentData(
					self.data["project"],
					self.data["commit"]
				)
			except KeyError as e:
				data = {
					"resource": self.data["resource"],
					"project": self.data["project"],
					"commit": self.data["commit"]
				}
				self._extractContentData(data, True)
		else:
			# Get golang-project-packages artefact
			self._extractPackagesData(False)

			# Get golang-project-content-metadata artefact
			data = {
				"resource": self.data["resource"]
			}

			self._extractContentData(data, False)

		if self.golang_project_packages == {}:
			raise acttypes.ActDataError("Unable to get 'golang-project-packages' artefact")

		if self.golang_project_content_metadata == {}:
			raise acttypes.ActDataError("Unable to get 'golang-project-content-metadata' artefact")

		return True
