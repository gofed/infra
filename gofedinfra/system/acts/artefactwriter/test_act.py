import unittest
from infra.system.core.factory.fakefunctionfactory import FakeFunctionFactory
from .act import ArtefactWriterAct
from .fakeact import FakeArtefactWriterAct
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES

class ArtefactWriterActTest(unittest.TestCase):

	def test(self):

		data = {
			"timestamp": 1460997905,
			"distribution": {
				"product": "Fedora",
				"version": "rawhide"
			},
			"artefact": "golang-distribution-snapshot",
			"go_version": "",
			"builds": [{
				"build_ts": 1456165659,
				"rpms": [
					"golang-github-evanphx-json-patch-unit-test-0-0.6.gita1ba76c.fc24.i686.rpm",
					"golang-github-evanphx-json-patch-unit-test-0-0.6.gita1ba76c.fc24.x86_64.rpm",
					"golang-github-evanphx-json-patch-unit-test-0-0.6.gita1ba76c.fc24.armv7hl.rpm",
					"golang-github-evanphx-json-patch-devel-0-0.6.gita1ba76c.fc24.noarch.rpm",
					"golang-github-evanphx-json-patch-0-0.6.gita1ba76c.fc24.src.rpm"
				],
				"name": "golang-github-evanphx-json-patch",
				"build": "golang-github-evanphx-json-patch-0-0.6.gita1ba76c.fc24"
			}]
		}

		a = ArtefactWriterAct()
		a.setData(data)
		# Don't execute the act, just return empty data
		self.assertEqual(a.getData(), {})

		# Execute the act with fake plugins
		a.ff = FakeFunctionFactory()
		a.execute()
		a.getData()

		fa = FakeArtefactWriterAct()
		a.setData(data)
		a.execute()
		a.getData()
