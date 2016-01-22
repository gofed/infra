import unittest
from golang_project_info_fedora import GolangProjectInfoFedoraKeyGenerator
from golang_project_to_package_name import GolangProjectToPackageNameKeyGenerator
from golang_ipprefix_to_package_name import GolangIPPrefixToPackageNameKeyGenerator

class GolangProjectInfoFedoraTest(unittest.TestCase):
	def test(self):
		input = {"artefact": "golang-project-info-fedora", "distribution": "f23", "project": "github.com/coreos/etcd", "commit": "729b530c489a73532843e664ae9c6db5c686d314", "last-updated": "2015-12-12"}
		expected = "golang-project-info-fedora:github.com/coreos/etcd:f23"

		generator = GolangProjectInfoFedoraKeyGenerator()
		current = generator.generate(input)

		self.assertEqual(current, expected)

class GolangProjectToPackageNameTest(unittest.TestCase):
	def test(self):
		input = {"artefact": "golang-project-to-package-name", "product": "Fedora", "distribution": "f22", "project": "github.com/coreos/etcd", "name": "etcd"}
		expected = "golang-project-to-package-name:Fedora:f22:github.com/coreos/etcd"

		generator = GolangProjectToPackageNameKeyGenerator()
		current = generator.generate(input)

		self.assertEqual(current, expected)

class GolangIPPrefixToPackageNameTest(unittest.TestCase):
	def test(self):
		input = {"artefact": "golang-ipprefix-to-package-name", "product": "Fedora", "distribution": "f22", "ipprefix": "github.com/coreos/etcd", "name": "etcd"}
		expected = "golang-ipprefix-to-package-name:Fedora:f22:github.com/coreos/etcd"

		generator = GolangIPPrefixToPackageNameKeyGenerator()
		current = generator.generate(input)

		self.assertEqual(current, expected)

