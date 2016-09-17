from infra.system.plugins.gosymbolsextractor.extractor import GoSymbolsExtractor
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator
import logging
from infra.system.helpers.utils import getScriptDir
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API
)

from infra.system.helpers.artefactdecomposer import ArtefactDecomposer
from gofedlib.go.importpath.parserbuilder import ImportPathParserBuilder

class DistributionGoSymbolsExtractor(GoSymbolsExtractor):

	def __init__(self):
		GoSymbolsExtractor.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__)
		)

		self.product = ""
		self.distribution = ""
		self.rpm = ""
		self.build = ""

		self._packages = {}
		self._exported_api = {}

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
		return [
			self._packages,
			self._exported_api
		]

		# TODO(jchaloup): move validation to unit-tests
		#validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES)
		#if not validator.validate(data[0]):
		#	logging.error("%s is not valid" % ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES)
		#	return {}


		# TODO(jchaloup): move validation to unit-tests
		#validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API)
		#if not validator.validate(data[1]):
		#	logging.error("%s is not valid" % ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API)
		#	return {}

	def _generateGolangProjectDistributionPackagesArtefact(self):
		artefact = GoSymbolsExtractor._generateGolangProjectPackagesArtefact(self)

		artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES
		artefact["product"] = self.product
		artefact["distribution"] = self.distribution
		artefact["rpm"] = self.rpm
		artefact["build"] = self.build
		artefact["commit"] = self.commit

		ad = ArtefactDecomposer(ImportPathParserBuilder().buildDefault())
		return ad.decomposeArtefact(artefact)

	def _generateGolangProjectDistributionExportedAPI(self):
		artefact = GoSymbolsExtractor._generateGolangProjectExportedAPI(self)

		artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API
		artefact["product"] = self.product
		artefact["distribution"] = self.distribution
		artefact["rpm"] = self.rpm
		artefact["build"] = self.build
		artefact["commit"] = self.commit

		ad = ArtefactDecomposer(ImportPathParserBuilder().buildDefault())
		return ad.decomposeArtefact(artefact)

	def execute(self):
		ret = GoSymbolsExtractor.execute(self)
		if not ret:
			return False

		try:
			self._packages = self._generateGolangProjectDistributionPackagesArtefact()
		except ValueError:
			return False

		try:
			self._exported_api = self._generateGolangProjectDistributionExportedAPI()
		except ValueError:
			return False

		return True

