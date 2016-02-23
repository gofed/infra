from infra.system.core.meta.metaprocessor import MetaProcessor
import git
import time
import logging
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator
from infra.system.helpers.schema_validator import SchemaValidator
from infra.system.helpers.utils import getScriptDir
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO, ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT

class GitCommitExtractor(MetaProcessor):

	def __init__(self):
		self.data = []
		self.input_validated = False
		self.project = ''
		self.repository = ''
		self.repository_directory = ''
		self.clone_url = ''
		self.start_date = ''
		self.end_date = ''
		self.branches = []
		self.commits = set([])

	def setData(self, data):
		self.input_validated = False
		if not self._validateInput(data):
			return False

		self.project = data['project']
		self.repository = data['repository']
		self.repository_directory = data['repository_directory']
		self.clone_url = data['clone_url']
		self.branches = []
		self.commits = set([])

		if 'start_date' in data:
			self.start_date = data['start_date']
		else:
			self.start_date = '1970-01-01'
		if 'end_date' in data:
			self.end_date = data['end_date']
		else:
			self.end_date = time.strftime('%Y-%m-%d')
		return True

	def _generateGolangProjectRepositoryInfo(self):
		data = {}
		data['artefact'] = ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO
		data['project'] = self.project
		data['repository'] = self.repository
		data['clone_url'] = self.clone_url
		data['branches'] = self.branches
		data['commits'] = [ x.hexsha for x in self.commits ]
		return data

	def _generateGolangProjectRepositoryCommit(self, commit):
		data = {}
		data['artefact'] = ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT
		data['repository'] = self.repository
		data['commit'] = commit.hexsha
		data['adate'] = time.strftime('%Y-%m-%d', time.gmtime(commit.authored_date))
		data['cdate'] = time.strftime('%Y-%m-%d', time.gmtime(commit.committed_date))
		data['author'] = commit.author.name + ' <' + commit.author.email + '>'
		data['message'] = commit.message
		return data

	def getData(self):
		if not self.input_validated:
			return []
		data = []
		for i, commit in enumerate(self.commits):
			data.append(self._generateGolangProjectRepositoryCommit(commit))
			validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT)
			if not validator.validate(data[i]):
				logging.error('%s is not valid' % ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT)
				return {}

		data.append(self._generateGolangProjectRepositoryInfo())
		validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO)
		if not validator.validate(data[-1]):
			logging.error('%s is not valid' % ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO)
			return {}
		return data

	def _validateInput(self, data):
		validator = SchemaValidator()
		schema = '%s/input_schema.json' % getScriptDir(__file__)
		self.input_validated = validator.validateFromFile(schema, data)
		return self.input_validated

	def execute(self):
		repo = git.Repo(self.repository_directory)
		self.branches = [ x.name for x in repo.branches ]
		for branch in self.branches:
			self.commits = self.commits | set(repo.iter_commits(branch, since=self.start_date))

		self.commits = set([ x for x in self.commits if time.strftime('%Y-%m-%d', time.gmtime(x.committed_date)) <= self.end_date ])
		return True
