import unittest

from .analyzer import GoApiDiff

class GoApiDiffTest(unittest.TestCase):

	def test(self):

		data = {
			"exported_api_1": {
				"project": "example",
				"commit": "0000",
				"artefact": "golang-project-exported-api",
				"packages": []
			},
			"exported_api_2": {
				"project": "example",
				"commit": "0000",
				"artefact": "golang-project-exported-api",
				"packages": []
			}
		}

		expected = {
			'project': 'example',
			'commit2': '0000',
			'artefact': 'golang-projects-api-diff',
			'commit1': '0000',
			'data': {}
		}

		a = GoApiDiff()
		a.setData(data)
		# don't execute, just get empty data
		self.assertEqual(a.getData(), expected)
