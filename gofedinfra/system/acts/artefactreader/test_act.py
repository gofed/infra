import unittest
from infra.system.core.factory.fakefunctionfactory import FakeFunctionFactory
from .act import ArtefactReaderAct
from .fakeact import FakeArtefactReaderAct
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES

class ArtefactReaderActTest(unittest.TestCase):

	def test(self):

		data = {
			"distribution": {
				"product": "Fedora",
				"version": "rawhide"
			},
			"artefact": "golang-distribution-snapshot"
		}

		a = ArtefactReaderAct()
		a.setData(data)
		# Don't execute the act, just return empty data
		self.assertEqual(a.getData(), {})

		# Execute the act with fake plugins
		a.ff = FakeFunctionFactory()
		a.execute()
		a.getData()

		fa = FakeArtefactReaderAct()
		a.setData(data)
		a.execute()
		a.getData()
