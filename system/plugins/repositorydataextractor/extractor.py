from infra.system.core.meta.metaprocessor import MetaProcessor
import time
import datetime
import logging
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator
from infra.system.helpers.schema_validator import SchemaValidator
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO, ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT

from gofedlib.utils import getScriptDir
from gofedlib.utils import dateToTimestamp
from gofedlib.repository.repositoryclientbuilder import RepositoryClientBuilder

class RepositoryDataExtractor(MetaProcessor):

	def __init__(self, input_schema = "%s/input_schema.json" % getScriptDir(__file__)):
		MetaProcessor.__init__(
			self,
			input_schema
		)

		self.repository = {}
		self.repository_directory = ''
		self.start_date = ''
		self.end_date = ''
		self.commit = ''

		self.branches = []
		self.commits = {}

	def setData(self, data):
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
			self.end_date = int(time.time() + 86400)

		if 'start_timestamp' in data:
			self.start_date = data["start_timestamp"]

		if 'end_timestamp' in data:
			self.end_date = data["end_timestamp"]

		# Check single commit only?
		self.commit = ""
		if 'commit' in data:
			self.commit = data["commit"]

		# Extract data from a single branch?
		self.branch = ""
		if 'branch' in data:
			self.branch = data["branch"]

		return True

	def _generateGolangProjectRepositoryInfo(self, branches):
		data = {
			"artefact": ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO,
			"repository": self.repository,
			"branches": []
		}

		for branch in branches:
			data["branches"].append({
				"branch": branch,
				"commits": branches[branch]
			})

		start_date = self.end_date
		end_date = self.start_date
		for branch in self.commits:
			for commit in self.commits[branch]:
				start_date = min(start_date, self.commits[branch][commit]["cdate"])
				end_date = max(end_date, self.commits[branch][commit]["cdate"])

		data["coverage"] = [{"start": start_date, "end": end_date}]

		return data

	def _generateGolangProjectRepositoryCommit(self, commit):
		data = {}

		data['artefact'] = ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT
		data['repository'] = self.repository
		data['commit'] = commit["hexsha"]

		# keep timestamps
		data['adate'] = commit["adate"]
		data['cdate'] = commit["cdate"]
		data['author'] = commit["author"]
		data['message'] = commit["message"]

		return data

	def getData(self):
		if self.commit != "":
			return self._generateGolangProjectRepositoryCommit(self.commits[""])

		commits_data = {}
		branches = {}
		# TODO(jchaloup) this is quite redundant, make it better!!!
		for branch in self.commits:
			for commit in self.commits[branch]:
				try:
					branches[branch].append(commit)
				except KeyError:
					branches[branch] = [commit]

				if commit in commits_data:
					continue

				commits_data[commit] = self._generateGolangProjectRepositoryCommit(self.commits[branch][commit])

		# from all branches (up to master) filter out all commits that are already covered in master branch
		if "master" in branches:
			for branch in filter(lambda l: l != "master", branches.keys()):
				branches[branch] = list(set(branches[branch]) - set(branches["master"]))

		# TODO(jchaloup): move validation to unit-tests
		#for commit in commits_data:
		#	validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT)
		#	if not validator.validate(commits_data[commit]):
		#		logging.error('%s is not valid' % ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT)
		#		return {}

		info = self._generateGolangProjectRepositoryInfo(branches)
		#validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO)
		#if not validator.validate(info):
		#	logging.error('%s is not valid' % ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO)
		#	return {}

		repo_commits = []
		for commit in commits_data:
			repo_commits.append(commits_data[commit])

		return {
			"info": info,
			"commits": repo_commits,
			"branches": branches
		}

	def execute(self):
		repo_client = RepositoryClientBuilder().buildWithLocalClient(self.repository, self.repository_directory)

		if self.commit != "":
			self.commits[""] = repo_client.commit(self.commit)
			return True

		self.branches = repo_client.branches()

		self.commits = {}

		# just a single branch
		if self.branch != "":
			if self.branch not in self.branches:
				raise ValueError("Requested branch '%s' not found" % self.branch)

			self.commits[self.branch] = repo_client.commits(self.branch, since=self.start_date, to=self.end_date)
			return True

		# all branches
		for branch in self.branches:
			self.commits[branch] = repo_client.commits(branch, since=self.start_date, to=self.end_date)

		return True
