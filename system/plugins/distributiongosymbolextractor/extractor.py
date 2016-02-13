from system.plugins.gosymbolextractor.extractor import GoSymbolsExtractor
from system.helpers.artefact_schema_validator import ArtefactSchemaValidator
import logging
from system.helpers.utils import getScriptDir
from system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API
)

class DistributionGoSymbolExtractor(GoSymbolsExtractor):

	def __init__(self):
		GoSymbolsExtractor.__init__(self)

		self.product = ""
		self.distribution = ""
		self.rpm = ""
		self.build = ""
		self.input_schema = "%s/input_schema.json" % getScriptDir(__file__)

	def setData(self, data):
		if not GoSymbolsExtractor.setData(self, data):
			return False

		self.product = data["product"]
		self.distribution = data["distribution"]
		self.build = data["build"]
		self.rpm = data["rpm"]
		self.commit = data["commit"]

		return True

	def getData(self):
		if not self.input_validated:
			return []

		data = []

		data.append(self._generateGolangProjectDistributionPackagesArtefact())
		validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES)
		if not validator.validate(data[0]):
			logging.error("%s is not valid" % ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES)
			return {}

		data.append(self._generateGolangProjectDistributionExportedAPI())
		validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API)
		if not validator.validate(data[1]):
			logging.error("%s is not valid" % ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API)
			return {}

		return data

	def _generateGolangProjectDistributionPackagesArtefact(self):
		artefact = GoSymbolsExtractor._generateGolangProjectPackagesArtefact(self)

		artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES
		artefact["product"] = self.distribution
		artefact["distribution"] = self.product
		artefact["rpm"] = self.rpm
		artefact["build"] = self.build
		artefact["commit"] = self.commit

		return artefact

	def _generateGolangProjectDistributionExportedAPI(self):
		artefact = GoSymbolsExtractor._generateGolangProjectExportedAPI(self)

		artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API
		artefact["product"] = self.distribution
		artefact["distribution"] = self.product
		artefact["rpm"] = self.rpm
		artefact["build"] = self.build
		artefact["commit"] = self.commit

		return artefact

	def execute(self):
		return GoSymbolsExtractor.execute(self)
