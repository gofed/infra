import unittest

from .act import GoCodeInspectionAct
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES

class GoCodeInspectionActTest(unittest.TestCase):

	def test(self):

		data = {
			"type": "upstream_source_code",
			"project": "github.com/bradfitz/http2",
			"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
			"ipprefix": "github.com/bradfitz/http1"
		}

		a = GoCodeInspectionAct()
		a.setData(data)
		# Don't execute the act, just return empty data
		self.assertEqual(a.getData(), {ARTEFACT_GOLANG_PROJECT_PACKAGES: {}})
