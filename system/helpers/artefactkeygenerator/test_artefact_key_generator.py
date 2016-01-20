import unittest
from  golang_project_info_fedora import GolangProjectInfoFedoraKeyGenerator

class GolangProjectInfoFedoraTest(unittest.TestCase):
	def test(self):
		input = {"artefact": "golang-project-info-fedora", "distribution": "f23", "project": "github.com/coreos/etcd", "commit": "729b530c489a73532843e664ae9c6db5c686d314", "last-updated": "2015-12-12"}
		expected = "golang-project-info-fedora:github.com/coreos/etcd:f23"

		generator = GolangProjectInfoFedoraKeyGenerator()
		current = generator.generate(input)

		self.assertEqual(current, expected)
