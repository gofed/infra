import unittest
from .extractor import GoSymbolsExtractor

class GoSymbolsExtractorTest(unittest.TestCase):

	def test(self):

		data = {
			"resource": "fake/source/code/location",
			"repository": {
				"provider": "github",
				"username": "golang",
				"project": "example"
			},
			"commit": "729b530c489a73532843e664ae9c6db5c686d314",
			"ipprefix": "github.com/golang/example"
		}

		expected = [{
			"repository": {
				"provider": "github",
				"username": "golang",
				"project": "example"
			},
			'commit': data["commit"],
			'artefact': 'golang-project-packages',
			'data': {},
			'ipprefix': data["ipprefix"]
		}, {
			"repository": {
				"provider": "github",
				"username": "golang",
				"project": "example"
			},
			'commit': data["commit"],
			'artefact': 'golang-project-exported-api',
			'packages': []
		}]

		e = GoSymbolsExtractor()

		e.setData(data)
		# Don't execute, just retrieve empty data
		self.assertEqual(e.getData(), expected)
