from infra.system.core.meta.metaprocessor import MetaProcessor
import time
import datetime
import logging
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator
from infra.system.helpers.schema_validator import SchemaValidator
from infra.system.helpers.utils import getScriptDir
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO, ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT

from gofed_lib.github.client import GithubLocalClient
from gofed_lib.utils import dateToTimestamp

class RepositoryDataExtractor(MetaProcessor):

	def __init__(self):
		self.input_validated = False

		self.repository = {}
		self.repository_directory = ''
		self.start_date = ''
		self.end_date = ''

		self.branches = []
		self.commits = {}

	def setData(self, data):
		self.input_validated = False
		if not self._validateInput(data):
			return False

		self.repository = data['repository']
		self.repository_directory = data['resource']

		# TODO(jchaloup): check the date is in required format
		if 'start_date' in data:
			self.start_date = dateToTimestamp(data["start_date"])
		else:
			self.start_date = dateToTimestamp('1970-01-02')

		if 'end_date' in data:
			self.end_date = dateToTimestamp(data["end_date"])
		else:
			self.end_date = time.mktime((datetime.date.today() + datetime.timedelta(hours=24)).timetuple())

		return True

	def _generateGolangProjectRepositoryInfo(self):
		data = {}
		data['artefact'] = ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO
		data['repository'] = self.repository
		data['branches'] = self.branches

		commits = set([])
		for branch in self.commits:
			commits = commits | set(self.commits[branch].keys())

		data['commits'] = list(commits)

		return data

	def _generateGolangProjectRepositoryCommit(self, commit):
		data = {}

		data['artefact'] = ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT
		data['repository'] = self.repository
		data['commit'] = commit["hexsha"]
		data['adate'] = time.strftime('%Y-%m-%d', time.gmtime(commit["adate"]))
		data['cdate'] = time.strftime('%Y-%m-%d', time.gmtime(commit["cdate"]))
		data['author'] = commit["author"]
		data['message'] = commit["message"]

		return data

	def getData(self):
		if not self.input_validated:
			return []

		data = []

		data.append(self._generateGolangProjectRepositoryInfo())
		validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO)
		if not validator.validate(data[0]):
			logging.error('%s is not valid' % ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO)
			return {}

		commits_data = {}
		# TODO(jchaloup) this is quite redundant, make it better!!!
		for branch in self.commits:
			for commit in self.commits[branch]:
				if commit in commits_data:
					continue

				commits_data[commit] = self._generateGolangProjectRepositoryCommit(self.commits[branch][commit])

		# TODO(jchaloup): move validation to unit-tests
		#for commit in commits_data:
		#	validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT)
		#	if not validator.validate(commits_data[commit]):
		#		logging.error('%s is not valid' % ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT)
		#		return {}

		return data

	def _validateInput(self, data):
		validator = SchemaValidator()
		schema = '%s/input_schema.json' % getScriptDir(__file__)
		self.input_validated = validator.validateFromFile(schema, data)
		return self.input_validated

	def execute(self):
		client = GithubLocalClient(self.repository_directory)
		self.branches = client.branches()

		self.commits = {}
		for branch in self.branches:
			self.commits[branch] = client.commits(branch, since=self.start_date, to=self.end_date)

		return True
