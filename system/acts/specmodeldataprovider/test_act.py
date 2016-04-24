import unittest
from infra.system.core.factory.fakefunctionfactory import FakeFunctionFactory
from .act import SpecModelDataProviderAct
from .fakeact import FakeSpecModelDataProviderAct
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES, ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA

class SpecModelDataProviderActTest(unittest.TestCase):

	def test(self):

		data = {
			"type": "upstream_source_code",
			"repository": {
				"provider": "github",
				"username": "bradfitz",
				"project": "bradfitz"
			},
			"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
			"ipprefix": "github.com/bradfitz/http2"
		}

		expected = {
			ARTEFACT_GOLANG_PROJECT_PACKAGES: {},
			ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA: {}
		}

		a = SpecModelDataProviderAct()
		a.setData(data)
		# Don't execute the act, just return empty data
		self.assertEqual(a.getData(), expected)

		# Execute the act with fake plugins
		a.ff = FakeFunctionFactory()
		a.execute()
		a.getData()

		fa = FakeSpecModelDataProviderAct()
		a.setData(data)
		a.execute()
		a.getData()

