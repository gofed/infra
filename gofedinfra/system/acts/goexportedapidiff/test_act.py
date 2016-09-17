import unittest
from infra.system.core.factory.fakefunctionfactory import FakeFunctionFactory
from .act import GoExportedApiDiffAct
from .fakeact import FakeGoExportedApiDiffAct
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECTS_API_DIFF
)

class GoExportedApiDiffActTest(unittest.TestCase):

	def test(self):

		data = {
			"reference": {
				"type": "upstream_source_code",
				"repository": {
					"provider": "github",
					"username": "bradfitz",
					"project": "http2"
				},
				"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f"
			},
			"compared_with": {
				"type": "upstream_source_code",
				"repository": {
					"provider": "github",
					"username": "bradfitz",
					"project": "http2"
				},
				"commit": "953b51136f12cb27503bec0f659432fd1fa97770"
			}
		}

		expected = {
			ARTEFACT_GOLANG_PROJECTS_API_DIFF: {}
		}

		a = GoExportedApiDiffAct()
		a.setData(data)
		# Don't execute the act, just return empty data
		self.assertEqual(a.getData(), expected)

		# Execute the act with fake plugins
		a.ff = FakeFunctionFactory()
		a.execute()
		a.getData()

		fa = FakeGoExportedApiDiffAct()
		a.setData(data)
		a.execute()
		a.getData()
