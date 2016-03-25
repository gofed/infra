from infra.system.plugins.gitcommitextractor.extractor import RepositoryDataExtractor
from git.objects.commit import Commit
from git.util import Actor

class FakeRepositoryDataExtractor(RepositoryDataExtractor):

	def __init__(self):
		RepositoryDataExtractor.__init__(self)

	def setData(self, data):
		data = {
			'repository': {
				"provider": "github",
				"username": "username",
				"project": "project"
			},
			'resource': 'example',
			'start_date': '1970-01-02',
			'end_date': '2016-01-01'
		}
		RepositoryDataExtractor.setData(self, data)

	def getData(self):
		return RepositoryDataExtractor.getData(self)

	def execute(self):
		self.branches = ['first', 'second']
		self.commits = {
			"first": {"92a73e727b28de00cf9ebb5a40204901f927663b": {
					"hexsha": "92a73e727b28de00cf9ebb5a40204901f927663b",
					"adate": 1455110000,
					"cdate": 1455110000,
					"author": "Dominika Hodovska <dhodovsk@example.com>",
					"message": "first example commit"
					}
			},
			"second": {"f8d9f8sd8fs08f0s8df08sf8sfsdf801f927663b": {
					"hexsha": "f8d9f8sd8fs08f0s8df08sf8sfsdf801f927663b",
					"adate": 1455110000,
					"cdate": 1455110000,
					"author": "Dominika Hodovska <dhodovsk@example.com>",
					"message": "second example commit"
					}
			}
		}

		return True
