from golang_project_info_fedora_driver import GolangProjectInfoFedoraDriver
import unittest
import json

class GolangProjectInfoFedoraTest(unittest.TestCase):
	def test(self):

		input = {"artefact": "golang-project-info-fedora", "distribution": "f23", "project": "github.com/coreos/etcd", "commit": "729b530c489a73532843e664ae9c6db5c686d314", "last-updated": "2015-12-12"}
		driver = GolangProjectInfoFedoraDriver()
		driver.store(input)
	
		expected = json.dumps(input)
		current = driver.retrieve(input)
	
		# value is a string, not json so no need to sorted it before comparison
		self.assertEqual(current, expected)
