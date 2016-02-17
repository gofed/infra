from system.core.meta.metaact import MetaAct
from system.resources.specifier import ResourceSpecifier
from system.resources import types
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES
from system.core.functions.types import FunctionNotFoundError, FunctionFailedError
from system.helpers.schema_validator import SchemaValidator
from system.helpers.utils import getScriptDir

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
		return self.golang_project_packages

	def execute(self):
		"""Impementation of concrete data processor"""
		if self.data["type"] == INPUT_TYPE_UPSTREAM_SOURCE_CODE:
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
		else:
			self.golang_project_packages = self._getArtefactFromData(
				ARTEFACT_GOLANG_PROJECT_PACKAGES,
				self.ff.bake("gosymbolsextractor").call(self.data)
			)

		if self.golang_project_packages == {}:
			return False

		# TODO(jchaloup): move exception handling to act user
		#except FunctionNotFoundError as e:
		#	logging.error("spec-model-data-provider-act: %s" % e)
		#	return False
		#except FunctionFailedError as e:
		#	logging.error("spec-model-data-provider-act: %s" % e)
		#	return False
		#except types.ResourceNotFoundError as e:
		#	logging.error("spec-model-data-provider-act: %s" % e)
		#	return False

		return True
