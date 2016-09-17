from infra.system.core.meta.metaprocessor import MetaProcessor
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECTS_API_DIFF
import logging
from gofedlib.utils import getScriptDir
from gofedlib.go.apidiff import apidiff

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

	api_2 is new
	api_1 is old

	Result of comparison is new - old, i,e, api_2 - api_1
	"""

	def __init__(self):
		MetaProcessor.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__),
			ref_schema_directory = "%s/../../artefacts/schemas" % getScriptDir(__file__)
		)

		self._exported_api1 = {}
		self._exported_api2 = {}

		self._apidiff = {}
		self._repository = {}
		self._commit1 = ""
		self._commit2 = ""

	def _validateInput(self, data):
		if not MetaProcessor._validateInput(self, data):
			return False

		# projects must be the same
		if data["exported_api_1"]["repository"] == data["exported_api_2"]["repository"]:
			self._repository = data["exported_api_1"]["repository"]

		return True

	def setData(self, data):
		"""Validation and data pre-processing"""
		if not self._validateInput(data):
			return False

		self._exported_api1 = data["exported_api_1"]["packages"]
		self._exported_api2 = data["exported_api_2"]["packages"]

		self._repository = data["exported_api_1"]["repository"]
		self._commit1 = data["exported_api_1"]["commit"]
		self._commit2 = data["exported_api_2"]["commit"]

		return True

	def getData(self):
		"""Validation and data post-processing"""
		return self._generateGolangProjectsAPIDiffArtefact()

	def _generateGolangProjectsAPIDiffArtefact(self):
		return {
			"artefact": ARTEFACT_GOLANG_PROJECTS_API_DIFF,
			"repository": self._repository,
			"commit1": self._commit1,
			"commit2": self._commit2,
			"data": self._apidiff
		}

	def execute(self):
		"""Impementation of concrete data processor"""
		try:
			self._apidiff = apidiff.GoApiDiff(
				self._exported_api1,
				self._exported_api2
			).runDiff().apiDiff()
		except ValueError as e:
			logging.error("GoApiDiff: %s" % e)
			return False

		return True

