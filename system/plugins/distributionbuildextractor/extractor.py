from infra.system.core.meta.metaprocessor import MetaProcessor
from infra.system.helpers.schema_validator import SchemaValidator
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator
from infra.system.helpers.utils import getScriptDir
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_INFO
)
import logging
import koji
import time

KOJISERVER = "http://koji.fedoraproject.org/kojihub/"


class DistributionBuildExtractor(MetaProcessor):

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

		self.project = data["project"]
		self.product = data["product"]
		self.distribution = data["distribution"]
		self.repository = data["repository"]
		self.clone_url = data["clone_url"]

		if 'start_date' in data:
			self.start_date = data['start_date']
		else:
			self.start_date = '1970-01-01'
		if 'end_date' in data:
			self.end_date = data['end_date']
		else:
			self.end_date = time.strftime('%Y-%m-%d')
		return True

	def getData(self):
		if not self.input_validated:
			return []

		data = []
		for i, build in enumerate(self.builds):
			data.append(self._generateGolangProjectDistributionBuild(build))
			validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD)
			if not validator.validate(data[i]):
				logging.error('%s is not valid' % ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD)
				return {}

		data.append(self._generateGolangProjectDistributionInfo())
		validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_INFO)
		if not validator.validate(data[-1]):
			logging.error('%s is not valid' % ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_INFO)
			return {}
		return data

	def _generateGolangProjectDistributionBuild(self, build):
		artefact = {}

		artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD

		artefact["bdate"] = build['bdate']
		artefact["author"] = build['author']
		artefact["build"] = build['name']
		artefact["architectures"] = list(build['architectures'])
		artefact["rpms"] = build['rpms']
		artefact["koji"] = "http://koji.fedoraproject.org/koji/buildinfo?buildID=" + str(build['id'])

		return artefact

	def _generateGolangProjectDistributionInfo(self):
		artefact = {}

		artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_INFO

		artefact["project"] = self.project
		artefact["product"] = self.product
		artefact["distribution"] = self.distribution
		artefact["repository"] = self.repository
		artefact["clone_url"] = self.clone_url
		artefact["builds"] = [x['name'] for x in self.builds]

		return artefact

	def execute(self):

		session = koji.ClientSession(KOJISERVER)
		builds = session.queryHistory(package=self.project)["tag_listing"]

		build_id_set = set([x['build_id'] for x in builds if self.distribution in x['tag.name']])

		for build_id in build_id_set:
			build_info = session.getBuild(build_id)
			bdate = build_info["completion_time"][:10]
			if bdate < self.start_date or bdate > self.end_date:
				continue
			build_rpms = session.listRPMs(build_id)
			build = {}
			build["id"] = build_id
			build["bdate"] = bdate
			build["author"] = build_info["owner_name"]
			build["name"] = build_info["nvr"]
			build["architectures"] = set([x['arch']for x in build_rpms])
			build["rpms"] = []
			for rpm in build_rpms:
				build["rpms"].append(rpm['nvr'] + '.' + rpm['arch'] + '.rpm')
			self.builds.append(build)

		return True
