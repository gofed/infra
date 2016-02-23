from infra.system.plugins.gitcommitextractor.extractor import GitCommitExtractor
from git.objects.commit import Commit
from git.util import Actor

class FakeGitCommitExtractor(GitCommitExtractor):

	def __init__(self):
		GitCommitExtractor.__init__(self)

	def setData(self, data):
		data = {'project': 'example',
				'repository': 'example',
				'repository_directory': 'example',
				'clone_url': 'example',
				'start_date': '1970-01-01',
				'end_date': '2016-01-01'}
		GitCommitExtractor.setData(self, data)

	def getData(self):
		return GitCommitExtractor.getData(self)

	def execute(self):
		self.branches = ['first', 'second']
		actor = Actor('Dominika Hodovska', 'dhodovsk@example.com')
		commit = Commit(None, 'O\x0f\x84H\xe1Z\xd0\xd0\xdeL\xb3\xe9\xd5\xda\x86\rX\x08\xdaF', authored_date=1455110000,
						committed_date=1455110000, author=actor, message='first example commit')
		self.commits.add(commit)
		commit = Commit(None, 'O\x0f\x84H\xe1Z\xd0\xe0\xdeL\xa3\xe9\xd5\xda\x86\rX\x08\xdaF', authored_date=155110000,
						committed_date=155110000, author=actor, message='second example commit')
		self.commits.add(commit)
		return True
