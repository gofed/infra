from system.core.meta.metaprocessor import MetaProcessor
from system.helpers.artefact_schema_validator import ArtefactSchemaValidator
from system.helpers.schema_validator import SchemaValidator
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECTS_API_DIFF
import logging
from system.helpers.utils import getScriptDir
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
		self.input_validated = False
		self.apidiff = None

	def _validateInput(self, data):
		validator = SchemaValidator("%s/../../artefacts/schemas" % getScriptDir(__file__))
		schema_file = "%s/input_schema.json" % getScriptDir(__file__)
		if not validator.validateFromFile(schema_file, data):
			return False

		# projects must be the same
		if data["exported_api_1"]["project"] != data["exported_api_2"]["project"]:
			logging.error("goapidiff: project1 != project2")
			# TODO(jchaloup): throw exception?
			return False

		return True

	def setData(self, data):
		"""Validation and data pre-processing"""
		self.input_validated = self._validateInput(data)
		if not self.input_validated:
			return False

		self.apidiff = goapidiff.GoApiDiff(
			data["exported_api_1"],
			data["exported_api_2"]
		)

		self.project = data["exported_api_1"]["project"]
		self.commit1 = data["exported_api_1"]["commit"]
		self.commit2 = data["exported_api_2"]["commit"]

		return True

	def getData(self):
		"""Validation and data post-processing"""
		if not self.input_validated:
			return {}

		return self._generateGolangProjectsAPIDiffArtefact()

	def _generateGolangProjectsAPIDiffArtefact(self):

		apidiff_obj = {
			"artefact": ARTEFACT_GOLANG_PROJECTS_API_DIFF,
			"project": self.project,
			"commit1": self.commit1,
			"commit2": self.commit2,
			"data": self.apidiff.getProjectsApiDiff()
		}

		return apidiff_obj

	def execute(self):
		"""Impementation of concrete data processor"""
		if not self.input_validated:
			logging.error("goapidiff: invalid input")
			return False

		return self.apidiff.runDiff()

