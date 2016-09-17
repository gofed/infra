import unittest
from .extractor import GoProjectContentMetadataExtractor

class GoProjectContentMetadataExtractorTest(unittest.TestCase):

	def test(self):

		data = {
			"resource": "fake/re/source",
			"repository": {
				"provider": "github",
				"username": "test",
				"project": "test.project"
			},
			"commit": "0000"
		}

		expected = {
			"repository": {
				"provider": "github",
				"username": "test",
				"project": "test.project"
			},
			'commit': '0000',
			'artefact': 'golang-project-content-metadata',
			'metadata': {}
		}

		e = GoProjectContentMetadataExtractor()
		e.setData(data)
		# don't execute the plugin, just get empty data
		self.assertEqual(e.getData(), expected)
