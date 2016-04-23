import unittest
from .extractor import GoProjectContentMetadataExtractor

class GoProjectContentMetadataExtractorTest(unittest.TestCase):

	def test(self):

		data = {
			"resource": "fake/re/source",
			"project": "test.project",
			"commit": "0000"
		}

		expected = {
			'project': 'test.project',
			'commit': '0000',
			'artefact': 'golang-project-content-metadata',
			'metadata': {}
		}

		e = GoProjectContentMetadataExtractor()
		e.setData(data)
		# don't execute the plugin, just get empty data
		self.assertEqual(e.getData(), expected)
