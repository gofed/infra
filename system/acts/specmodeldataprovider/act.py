from infra.system.core.meta.metaact import MetaAct
from infra.system.resources.specifier import ResourceSpecifier
from infra.system.resources import types
from infra.system.core.acts import types as acttypes
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES, ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA
from infra.system.core.functions.types import FunctionNotFoundError, FunctionFailedError
from infra.system.helpers.schema_validator import SchemaValidator
from infra.system.helpers.utils import getScriptDir
from gofed_lib.data2specmodeldata import Data2SpecModelData

import json

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

		self.data = data

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
		return [
			self.golang_project_packages,
			self.golang_project_content_metadata
		]

	def execute(self):
		"""Impementation of concrete data processor"""
		if self.data["type"] == INPUT_TYPE_UPSTREAM_SOURCE_CODE:
			# Get golang-project-packages artefact
			ok, self.golang_project_packages = self.ff.bake("etcdstoragereader").call({
				"artefact": ARTEFACT_GOLANG_PROJECT_PACKAGES,
				"project": self.data["project"],
				"commit": self.data["commit"]
			})
			if not ok:
				self.golang_project_packages = self._getArtefactFromData(
					ARTEFACT_GOLANG_PROJECT_PACKAGES,
					self.ff.bake("gosymbolsextractor").call(self.data)
				)

				# store the data
				# TODO(jchaloup): check it was actually successful
				# TODO(jchaloup): this is for testing only, remove after switching to production
				self.ff.bake("etcdstoragewriter").call(self.golang_project_packages)

			# Get golang-project-content-metadata
			ok, self.golang_project_content_metadata = self.ff.bake("etcdstoragereader").call({
				"artefact": ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA,
				"project": self.data["project"],
				"commit": self.data["commit"]
			})
			if ok:			
				data = {
					"resource": self.data["resource"],
					"project": self.data["project"],
					"commit": self.data["commit"]
				}
				self.golang_project_content_metadata = self.ff.bake("goprojectcontentmetadataextractor").call(data)
				# store the data
				# TODO(jchaloup): check it was actually successful
				# TODO(jchaloup): this is for testing only, remove after switching to production
				self.ff.bake("etcdstoragewriter").call(self.golang_project_content_metadata)

		else:
			# Get golang-project-packages artefact
			self.golang_project_packages = self._getArtefactFromData(
				ARTEFACT_GOLANG_PROJECT_PACKAGES,
				self.ff.bake("gosymbolsextractor").call(self.data)
			)

			# Get golang-project-content-metadata artefact
			data = {
				"resource": self.data["resource"]
			}
			self.golang_project_content_metadata = self.ff.bake("goprojectcontentmetadataextractor").call(data)

		if self.golang_project_packages == {}:
			raise acttypes.ActDataError("Unable to get 'golang-project-packages' artefact")

		if self.golang_project_content_metadata == {}:
			raise acttypes.ActDataError("Unable to get 'golang-project-content-metadata' artefact")

		return True
