import unittest
from .extractor import SpecDataExtractor

class SpecDataExtractorTest(unittest.TestCase):

	def test(self):

		data = {
			"product": "Fedora",
			"distribution": "f24",
			"package": "test_package",
			"resource": "random/test/resource"
		}

		expected = [{
			'project': '',
			'commit': '',
			'artefact': 'golang-project-info-fedora',
			'distribution': data["distribution"],
			'last-updated': ''
		}, {
			'project': '',
			'distribution': data["distribution"],
			'artefact': 'golang-project-to-package-name',
			'product': data["product"],
			'name': data["package"]
		}, {
			'distribution': data["distribution"],
			'artefact': 'golang-ipprefix-to-package-name',
			'product': data["product"],
			'name': data["package"],
			'ipprefix': ''
		}]

		e = SpecDataExtractor()
		e.setData(data)
		# Don't execute the plugin, just return empty data
		self.assertEqual(e.getData(), expected)
