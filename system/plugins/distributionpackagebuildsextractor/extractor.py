from infra.system.core.meta.metaprocessor import MetaProcessor
from infra.system.helpers.schema_validator import SchemaValidator
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator
from infra.system.helpers.utils import getScriptDir
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS
)
import logging
import koji
import time
from gofed_lib.utils import dateToTimestamp

from gofed_lib.kojiclient import KojiClient

KOJISERVER = "http://koji.fedoraproject.org/kojihub/"


class DistributionPackageBuildsExtractor(MetaProcessor):

	def __init__(self):
		self.input_validated = False

		self.project = ""
		self.product = ""
		self.distribution = ""
		self.repository = ""
		self.clone_url = ""
		self.start_date = ""
		self.end_date = ""

		self.builds = []

	def _validateInput(self, data):
		validator = SchemaValidator()
		schema = "%s/input_schema.json" % getScriptDir(__file__)
		self.input_validated = validator.validateFromFile(schema, data)
		return self.input_validated

	def setData(self, data):
		self.input_validated = False
		if not self._validateInput(data):
			return []

		self.package = data["package"]
		self.product = data["product"]
		self.distribution = data["distribution"]

		# TODO(jchaloup): check the date is in required format
		if 'start_date' in data:
			self.start_ts = dateToTimestamp(data["start_date"])
		else:
			self.start_ts = dateToTimestamp('1970-01-02')

		if 'end_date' in data:
			self.end_ts = dateToTimestamp(data["end_date"])
		else:
			self.end_ts = int(time.time() + 86400)

		if 'start_timestamp' in data:
			self.start_ts = data["start_timestamp"]

		if 'end_timestamp' in data:
			self.end_ts = data["end_timestamp"]

		return True

	def getData(self):
		if not self.input_validated:
			return []

		data = []
		for build in self.builds:
			artefact = self._generateGolangProjectDistributionBuild(self.builds[build])
			validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD)
			if not validator.validate(artefact):
				logging.error('%s is not valid' % ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD)
				return {}
			data.append(artefact)

		artefact = self._generateGolangProjectDistributionPackageBuilds()
		validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS)
		if not validator.validate(artefact):
			logging.error('%s is not valid' % ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS)
			return {}

		data.append(artefact)

		return data

	def _generateGolangProjectDistributionBuild(self, build):
		artefact = {}

		artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD

		artefact["build_date"] = build['build_date']
		artefact["author"] = build['author']
		artefact["name"] = build['name']
		artefact["architectures"] = list(build['architectures'])
		artefact["rpms"] = build['rpms']
		artefact["build_url"] = "http://koji.fedoraproject.org/koji/buildinfo?buildID=" + str(build['id'])

		return artefact

	def _generateGolangProjectDistributionPackageBuilds(self):
		artefact = {}

		artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS

		artefact["package"] = self.package
		artefact["product"] = self.product
		artefact["distribution"] = self.distribution
		artefact["builds"] = self.builds.keys()

		return artefact

	def execute(self):

		self.builds = KojiClient().getPackageBuilds(
			self.distribution,
			self.package,
			since = self.start_ts,
			to = self.end_ts
		 )

		return True
