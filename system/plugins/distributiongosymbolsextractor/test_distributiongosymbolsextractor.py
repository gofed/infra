import unittest
from .extractor import DistributionGoSymbolsExtractor

class DistributionGoSymbolsExtractorTest(unittest.TestCase):

	def test(self):

		data = {
			"resource": "fake/source/code/location",
			"commit": "729b530c489a73532843e664ae9c6db5c686d314",
			"product": "Fedora",
			"distribution": "f23",
			"build": "example-2.2.4-1.fc24",
			"rpm": "example-devel-2.2.4-1.fc24.noarch.rpm"
		}

		e = DistributionGoSymbolsExtractor()
		e.setData(data)
		# Don't execute, just retrieve empty data
		e.getData()
