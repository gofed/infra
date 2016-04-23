import unittest
from infra.system.core.factory.fakefunctionfactory import FakeFunctionFactory
from .act import ArtefactReaderAct
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES

class ArtefactReaderActTest(unittest.TestCase):

	def test(self):

		data = {
			"artefact": "golang-project-exported-api",
			"project": "github.com/coreos/etcd",
			"commit": "b4bddf685b26b4aa70e939445044bdeac822d042"
		}

		a = ArtefactReaderAct()
		a.setData(data)
		# Don't execute the act, just return empty data
		self.assertEqual(a.getData(), {})

		# Execute the act with fake plugins
		a.ff = FakeFunctionFactory()
		a.execute()
		a.getData()

