from infra.system.core.meta.metaact import MetaAct
from infra.system.resources.specifier import ResourceSpecifier
from infra.system.resources import types
from infra.system.helpers.utils import getScriptDir
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES

INPUT_TYPE_UPSTREAM_SOURCE_CODE = "upstream_source_code"
INPUT_TYPE_USER_DIRECTORY = "user_directory"

class GoCodeInspectionAct(MetaAct):

	def __init__(self):
		MetaAct.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__)
		)

		self._golang_project_packages = {}

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
			# any project is valid project for user directory
			self.data["project"] = "."
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
			ARTEFACT_GOLANG_PROJECT_PACKAGES: self._golang_project_packages
		}

	def _extractData(self, store = False):
		artefacts = self.ff.bake("gosymbolsextractor").call(self.data)
		self._golang_project_packages = self._getArtefactFromData(
			ARTEFACT_GOLANG_PROJECT_PACKAGES,
			artefacts
		)

		if not store:
			return

		if not self.store_artefacts:
			return

		for artefact in artefacts:
			try:
				data = self.ff.bake(self.write_storage_plugin).call(artefact)
			except IOError as e:
				logging.error(e)
				# Just log the data could not be stored

	def _readData(self, project, commit):
		return self.ff.bake(self.read_storage_plugin).call({
			"artefact": ARTEFACT_GOLANG_PROJECT_PACKAGES,
			"project": project,
			"commit": commit
		})

	def execute(self):
		"""Impementation of concrete data processor"""
		if self.retrieve_artefacts and self.data["type"] == INPUT_TYPE_UPSTREAM_SOURCE_CODE:
			try:
				self._golang_project_packages = self._readData(
					self.data["project"],
					self.data["commit"]
				)
			except KeyError as e:
				self._extractData(True)
		else:
				self._extractData(False)

		if self._golang_project_packages == {}:
			return False

		return True
