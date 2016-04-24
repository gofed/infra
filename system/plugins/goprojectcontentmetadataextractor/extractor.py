from infra.system.core.meta.metaprocessor import MetaProcessor
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA
from gofed_lib.go.contentmetadataextractor import ContentMetadataExtractor
from gofed_lib.utils import getScriptDir

class GoProjectContentMetadataExtractor(MetaProcessor):

	def __init__(self, input_schema = "%s/input_schema.json" % getScriptDir(__file__)):
		MetaProcessor.__init__(
			self,
			input_schema
		)

		self.contentmetadataextractor = None
		self.resource = ""
		self.repository = {}
		self.commit = ""

		self._metadata = {}

	def setData(self, data):

		if not self._validateInput(data):
			return False

		self.resource = data["resource"]
		if "repository" in data:
			self.repository = data["repository"]

		if "commit" in data:
			self.commit = data["commit"]

		self.contentmetadataextractor = ContentMetadataExtractor(self.resource)

		return True

	def execute(self):
		self.contentmetadataextractor.extract()
		data = self.contentmetadataextractor.projectContentMetadata()
		self._metadata = data["metadata"]
		return True

	def getData(self):
		return self._generateGolangProjectContentMetadataArtefact(self._metadata)

	def _generateGolangProjectContentMetadataArtefact(self, metadata):
		return {
			"artefact": ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA,
			"repository": self.repository,
			"commit": self.commit,
			"metadata": metadata
		}
