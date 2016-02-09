from system.helpers.artefact_schema_validator import ArtefactSchemaValidator
import logging
from system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API
)
from system.plugins.gosymbolextractor.fake_extractor import FakeGoSymbolExtractor


class FakeDistributionGoSymbolExtractor(FakeGoSymbolExtractor):

	def __init__(self):
		self.product = ""
		self.distribution = ""
		self.rpm = ""
		self.build = ""
		FakeGoSymbolExtractor.__init__(self)

	def setData(self, data):
		self.product = "Fedora"
		self.distribution = "f23"
		self.build = "example-2.2.4-1.fc24"
		self.rpm = "example-devel-2.2.4-1.fc24.noarch.rpm"
		return FakeGoSymbolExtractor.setData(self, data)

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
		artefact = FakeGoSymbolExtractor._generateGolangProjectPackagesArtefact(self)

		artefact["product"] = self.distribution
		artefact["distribution"] = self.product
		artefact["rpm"] = self.rpm
		artefact["build"] = self.build

		return artefact

	def _generateGolangProjectDistributionExportedAPI(self):
		artefact = FakeGoSymbolExtractor._generateGolangProjectExportedAPI(self)

		artefact["product"] = self.distribution
		artefact["distribution"] = self.product
		artefact["rpm"] = self.rpm
		artefact["build"] = self.build

		return artefact

	def execute(self):
		return FakeGoSymbolExtractor.execute(self)
