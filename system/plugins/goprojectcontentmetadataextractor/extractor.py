from infra.system.core.meta.metaprocessor import MetaProcessor
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA
from gofed_lib.contentmetadataextractor import ContentMetadataExtractor
from infra.system.helpers.utils import getScriptDir

class GoProjectContentMetadaExtractor(MetaProcessor):

	def __init__(self, input_schema = "%s/input_schema.json" % getScriptDir(__file__)):
		MetaProcessor.__init__(
			self,
			input_schema
		)

		self.contentmetadataextractor = None
		self.resource = ""
		self.project = ""
		self.commit = ""

	def setData(self, data):

		if not self._validateInput(data):
			return False

		self.resource = data["resource"]
		if "project" in data:
			self.project = data["project"]

		if "commit" in data:
			self.commit = data["commit"]

		self.contentmetadataextractor = ContentMetadataExtractor(self.resource)

		return True

	def execute(self):
		self.contentmetadataextractor.extract()
		return True

	def getData(self):
		data = self.contentmetadataextractor.getProjectContentMetadata()

		return self._generateGolangProjectContentMetadataArtefact(data)

	def _generateGolangProjectContentMetadataArtefact(self, data):
		return {
			"artefact": ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA,
			"project": self.project,
			"commit": self.commit,
			"metadata": data["metadata"]
		}
