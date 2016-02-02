from system.artefacts import artefacts
from artefactdriverfactory import ArtefactDriverFactory
from system.helpers.jsoncomparator import DirectJSONComparator

import unittest
import json

class ArtefactDriverTest(unittest.TestCase):

	def runTest(self, input, artefact = ""):

		if artefact == "":
			artefact = input["artefact"]

		driver = ArtefactDriverFactory().build(artefact)
		if driver == None:
			raise Exception("Driver not built")

		driver.store(input)

		expected = input
		current = driver.retrieve(input)
		self.assertEqual(DirectJSONComparator().equal(current, expected), True)

	def testGolangProjectInfoFedora(self):

		input = {
			"artefact": artefacts.ARTEFACT_GOLANG_PROJECT_INFO_FEDORA,
			"distribution": "f23",
			"project": "github.com/coreos/etcd",
			"commit": "729b530c489a73532843e664ae9c6db5c686d314",
			"last-updated": "2015-12-12"
		}

		self.runTest(input)

	def testGolangProjectToPackageName(self):

		input = {
			"artefact": artefacts.ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME,
			"product": "Fedora",
			"distribution": "f22",
			"project": "github.com/coreos/etcd",
			"name": "etcd"
		}

		self.runTest(input)

	def testGolangIPPrefixToPackageName(self):

		input = {
			"artefact": artefacts.ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME,
			"product": "Fedora",
			"distribution": "f22",
			"ipprefix": "github.com/coreos/etcd",
			"name": "etcd"
		}

		self.runTest(input)

