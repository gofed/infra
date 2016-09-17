from infra.system.core.meta.metaprocessor import MetaProcessor
from infra.system.helpers.schema_validator import SchemaValidator
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator
from gofedlib.utils import getScriptDir
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS
)
import logging
import time
from gofedlib.utils import dateToTimestamp

from gofedlib.distribution.clients.koji.client import KojiClient

class DistributionPackageBuildsExtractor(MetaProcessor):

	def __init__(self, input_schema = "%s/input_schema.json" % getScriptDir(__file__)):
		MetaProcessor.__init__(
			self,
			input_schema
		)

		self._client = KojiClient()

		self.project = ""
		self.product = ""
		self.distribution = ""
		self.repository = ""
		self.clone_url = ""
		self.start_date = ""
		self.end_date = ""

		self.builds = {}

	def setData(self, data):
		if not self._validateInput(data):
			return False

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
		package_builds = self._generateGolangProjectDistributionPackageBuilds()

		builds = []
		for build in self.builds:
			artefact = self._generateGolangProjectDistributionBuild(self.builds[build])
			#validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD)
			#if not validator.validate(artefact):
			#	logging.error('%s is not valid' % ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD)
			#	return {}
			builds.append(artefact)

		#validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS)
		#if not validator.validate(artefact):
		#	logging.error('%s is not valid' % ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS)
		#	return {}

		return {
			"package_builds": package_builds,
			"builds": builds
		}

	def _generateGolangProjectDistributionBuild(self, build):
		artefact = {}

		artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD
		artefact["product"] = self.product
		artefact["name"] = build['name']

		artefact["build_ts"] = build['build_ts']
		artefact["author"] = build['author']
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

		start_ts = self.end_ts
		end_ts = self.start_ts

		for build in self.builds:
			start_ts = min(start_ts, self.builds[build]["build_ts"])
			end_ts = max(end_ts, self.builds[build]["build_ts"])

		artefact["coverage"] = [{"start": start_ts, "end": end_ts}]

		return artefact

	def execute(self):

		self.builds = self._client.getPackageBuilds(
			self.distribution,
			self.package,
			since = self.start_ts,
			to = self.end_ts
		 )

		return True
