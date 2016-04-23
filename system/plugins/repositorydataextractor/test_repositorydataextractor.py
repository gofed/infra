import unittest
from .extractor import RepositoryDataExtractor

class RepositoryDataExtractorTest(unittest.TestCase):

	def test(self):

		data = {
			"repository": {
				"provider": "github",
				"username": "user",
				"project": "test"
			},
			"resource": "some/random/directory",
			"start_date": "2016-03-22",
			"end_date": "2016-03-26"
		}

		expected = {
			'info': {
				'artefact': 'golang-project-repository-info',
				'branches': [],
				'coverage': [{'start': 1458946800, 'end': 1458601200}],
				'repository': {
					'username': 'user',
					'project': 'test',
					'provider': 'github'
				}
			},
			'commits': [],
			'branches': {}
		}

		e = RepositoryDataExtractor()
		e.setData(data)
		self.assertEqual(e.getData(), expected)
