import unittest
from golang_project_info_fedora import GolangProjectInfoFedoraKeyGenerator
from golang_project_to_package_name import GolangProjectToPackageNameKeyGenerator
from golang_ipprefix_to_package_name import GolangIPPrefixToPackageNameKeyGenerator
from golang_project_exported_api import GolangProjectExportedAPIKeyGenerator
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_EXPORTED_API
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_INFO_FEDORA
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME
from system.artefacts.artefacts import ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME

class GolangProjectInfoFedoraTest(unittest.TestCase):
	def test(self):
		input = {"artefact": ARTEFACT_GOLANG_PROJECT_INFO_FEDORA, "distribution": "f23", "project": "github.com/coreos/etcd", "commit": "729b530c489a73532843e664ae9c6db5c686d314", "last-updated": "2015-12-12"}
		expected = "%s:%s:%s" % (ARTEFACT_GOLANG_PROJECT_INFO_FEDORA, input["project"], input["distribution"])

		generator = GolangProjectInfoFedoraKeyGenerator()
		current = generator.generate(input)

		self.assertEqual(current, expected)

class GolangProjectToPackageNameTest(unittest.TestCase):
	def test(self):
		input = {"artefact": ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME, "product": "Fedora", "distribution": "f22", "project": "github.com/coreos/etcd", "name": "etcd"}
		expected = "%s:%s:%s:%s" % (ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME, input["product"], input["distribution"], input["project"])

		generator = GolangProjectToPackageNameKeyGenerator()
		current = generator.generate(input)

		self.assertEqual(current, expected)

class GolangIPPrefixToPackageNameTest(unittest.TestCase):
	def test(self):
		input = {"artefact": ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME, "product": "Fedora", "distribution": "f22", "ipprefix": "github.com/coreos/etcd", "name": "etcd"}
		expected = "%s:%s:%s:%s" % (ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME, input["product"], input["distribution"], input["ipprefix"])

		generator = GolangIPPrefixToPackageNameKeyGenerator()
		current = generator.generate(input)

		self.assertEqual(current, expected)

class GolangProjectExportedAPITest(unittest.TestCase):
	def test(self):
		input = {"artefact": ARTEFACT_GOLANG_PROJECT_EXPORTED_API, "project": "github.com/coreos/etcd", "commit": "729b530c489a73532843e664ae9c6db5c686d314"}
		expected = "%s:%s:%s" % (ARTEFACT_GOLANG_PROJECT_EXPORTED_API, input["project"], input["commit"])

		generator = GolangProjectExportedAPIKeyGenerator()
		current = generator.generate(input)

		self.assertEqual(current, expected)

