from infra.system.core.meta.metaprocessor import MetaProcessor
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES, ARTEFACT_GOLANG_PROJECT_EXPORTED_API
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator
from infra.system.helpers.utils import getScriptDir
from gofedlib.go.symbolsextractor import extractor
from gofedlib.types import ExtractionError
import logging

CONFIG_SOURCE_CODE_DIRECTORY = "resource"
DATA_COMMIT = "commit"
DATA_IPPREFIX = "ipprefix"

class GoSymbolsExtractor(MetaProcessor):

	def __init__(self, input_schema = "%s/input_schema.json" % getScriptDir(__file__)):
		MetaProcessor.__init__(
			self,
			input_schema
		)

		"""Setting implicit flags"""
		# TODO(jchaloup): make verbose and skip_errors configurable from user input
		self.verbose = False
		self.skip_errors = True

		"""set implicit output"""
		# repository
		self.repository = ""
		# commit
		self.commit = ""
		# ipprefix
		self.ipprefix = ""

		"""set implicit states"""
		self.directory = ""

		self.gosymbolsextractor = None

		self._packages = {}
		self._exported_api = []

	def setVerbose(self):
		self.verbose = True

	def setSkipErrors(self):
		self.skip_errors = True

	def setData(self, data):
		self.data = data
		if not self._validateInput(data):
			return False

		# set directory with source codes to parse
		self.directory = data[CONFIG_SOURCE_CODE_DIRECTORY]

		# optional, repository, commit, ipprefix
		if "repository" in data:
			self.repository = data["repository"]

		if DATA_COMMIT in data:
			self.commit = data[DATA_COMMIT]

		if DATA_IPPREFIX in data:
			self.ipprefix = data[DATA_IPPREFIX]

		self.gosymbolsextractor = extractor.GoSymbolsExtractor(
			self.directory,
			verbose = self.verbose,
			skip_errors = self.skip_errors
		)

		return True

	def getData(self):
		data = []

		data.append(self._generateGolangProjectPackagesArtefact())
		# TODO(jchaloup): move validation to unit-tests
		#validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_PACKAGES)
		#if not validator.validate(data[0]):
		#	logging.error("%s is not valid" % ARTEFACT_GOLANG_PROJECT_PACKAGES)
		#	return {}

		data.append(self._generateGolangProjectExportedAPI())
		# TODO(jchaloup): move validation to unit-tests
		#validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_EXPORTED_API)
		#if not validator.validate(data[1]):
		#	logging.error("%s is not valid" % ARTEFACT_GOLANG_PROJECT_EXPORTED_API)
		#	return {}

		return data

	def _generateGolangProjectPackagesArtefact(self):
		artefact = {}

		# set artefact
		artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_PACKAGES

		# repository credentials
		if self.repository != "":
			artefact["repository"] = self.repository

		if self.commit != "":
			artefact["commit"] = self.commit

		if self.ipprefix != "":
			artefact["ipprefix"] = self.ipprefix

		artefact["data"] = self._packages

		return artefact

	def _generateGolangProjectExportedAPI(self):
		data = {}

		# set artefact
		data["artefact"] = ARTEFACT_GOLANG_PROJECT_EXPORTED_API

		# repository credentials
		data["repository"] = self.repository
		data["commit"] = self.commit

		data["packages"] = self._exported_api

		return data

	def execute(self):
		try:
			self.gosymbolsextractor.extract()
		except ExtractionError as e:
			logging.error("GoSymbolExtractor: %s" % e)
			return False
		except OSError as e:
			logging.error(e)
			return False

		self._packages = self.gosymbolsextractor.packages()
		self._exported_api = self.gosymbolsextractor.exportedApi()

		return True

