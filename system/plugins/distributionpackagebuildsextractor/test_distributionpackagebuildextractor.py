import unittest
from .extractor import DistributionPackageBuildsExtractor

class DistributionPackageBuildsExtractorTest(unittest.TestCase):

	def test(self):
		data = {
			"package": "etcd",
			"product": "Fedora",
			"distribution": "f24",
			"start_timestamp": 1400131190,
			"end_timestamp": 1460131190
		}

		expected = {
			'builds': [],
			'package_builds': {
				'artefact': 'golang-project-distribution-package-builds',
				'builds': [],
				'package': 'etcd',
				'product': 'Fedora',
				'coverage': [{'start': 1460131190, 'end': 1400131190}],
				'distribution': 'f24'
			}
		}

		e = DistributionPackageBuildsExtractor()
		e.setData(data)
		# don't execute the plugin, just let it return empty data
		self.assertEqual(e.getData(), expected)
