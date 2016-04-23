import unittest
from infra.system.core.factory.fakefunctionfactory import FakeFunctionFactory
from .act import ScanDistributionPackageAct
from .fakeact import FakeScanDistributionPackageAct
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD
)

class ScanDistributionPackageActTest(unittest.TestCase):

	def test(self):

		data = {
			"package": "etcd",
			"product": "Fedora",
			"distribution": "f24",
			"start_timestamp": 1400131190,
			"end_timestamp": 1460131190
		}

		expected = {
			ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS: {},
			ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD: {}
		}

		a = ScanDistributionPackageAct()
		a.setData(data)
		# Don't execute the act, just return empty data
		self.assertEqual(a.getData(), expected)

		# Execute the act with fake plugins
		a.ff = FakeFunctionFactory()
		a.execute()
		a.getData()

		fa = FakeScanDistributionPackageAct()
		a.setData(data)
		a.execute()
		a.getData()

