from infra.system.core.meta.metaprocessor import MetaProcessor
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECTS_API_DIFF
import logging
from infra.system.helpers.utils import getScriptDir
from gofed_lib import goapidiff

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
		MetaProcessor.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__),
			ref_schema_directory = "%s/../../artefacts/schemas" % getScriptDir(__file__)
		)
		self.apidiff = None

	def _validateInput(self, data):
		if not MetaProcessor._validateInput(self, data):
			return False

		# projects must be the same
		if data["exported_api_1"]["project"] != data["exported_api_2"]["project"]:
			logging.error("goapidiff: project1 != project2")
			# TODO(jchaloup): throw exception?
			return False

		return True

	def setData(self, data):
		"""Validation and data pre-processing"""
		if not self._validateInput(data):
			return False

		self.apidiff = goapidiff.GoApiDiff(
			data["exported_api_1"]["packages"],
			data["exported_api_2"]["packages"]
		)

		self.project = data["exported_api_1"]["project"]
		self.commit1 = data["exported_api_1"]["commit"]
		self.commit2 = data["exported_api_2"]["commit"]

		return True

	def getData(self):
		"""Validation and data post-processing"""
		return self._generateGolangProjectsAPIDiffArtefact()

	def _generateGolangProjectsAPIDiffArtefact(self):
		return {
			"artefact": ARTEFACT_GOLANG_PROJECTS_API_DIFF,
			"project": self.project,
			"commit1": self.commit1,
			"commit2": self.commit2,
			"data": self.apidiff.getProjectsApiDiff()
		}

	def execute(self):
		"""Impementation of concrete data processor"""
		try:
			self.apidiff.runDiff()
		except ValueError as e:
			logging.error("GoApiDiff: %s" % e)
			return False

		return True

