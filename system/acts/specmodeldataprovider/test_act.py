import unittest

from .act import SpecModelDataProviderAct
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES, ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA

class SpecModelDataProviderActTest(unittest.TestCase):

	def test(self):

		data = {
			"type": "upstream_source_code",
			"project": "github.com/bradfitz/http2",
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
