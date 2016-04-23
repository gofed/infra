import unittest
from infra.system.core.factory.fakefunctionfactory import FakeFunctionFactory
from .act import ScanUpstreamRepositoryAct
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO,
	ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT
)

class ScanUpstreamRepositoryActTest(unittest.TestCase):

	def test(self):

		data = {
			"repository": {
				"provider": "github",
				"username": "coreos",
				"project": "etcd"
			},
			"branch": "release-2.2",
			"start_date": "2016-03-15",
			"end_date": "2016-03-17"	
		}

		expected = {
			ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO: {},
			ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT: {}
		}

		a = ScanUpstreamRepositoryAct()
		a.setData(data)
		# Don't execute the act, just return empty data
		self.assertEqual(a.getData(), expected)

		# Execute the act with fake plugins
		a.ff = FakeFunctionFactory()
		a.execute()
		a.getData()

