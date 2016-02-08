from system.plugins.gosymbolextractor.extractor import GoSymbolExtractor
from system.helpers.utils import getScriptDir
import json
import os
class FakeGoSymbolExtractor(GoSymbolExtractor):
	def __init__(self):
		GoSymbolExtractor.__init__(self)

	def setData(self, data):
		self.project = "github.com/golang/example"
		self.commit = "729b530c489a73532843e664ae9c6db5c686d314"
		self.ipprefix = "github.com/golang/example"
		self.directory = "%s/example" % getScriptDir(__file__)
		self.noGodeps = []

		self.input_validated = True
		self.godeps_on = False

	def getData(self):
		return GoSymbolExtractor.getData(self)

	def execute(self):

		input_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fake_input.json')

		with open(input_file) as input_data:
			data = json.load(input_data)

		self.symbols = data["symbols"]
		self.symbols_position = data["symbols_position"]
		self.package_imports = data["package_imports"]
		self.imported_packages = data["imported_packages"]
		self.test_directories = data["test_directories"]
		self.package_imports_occurence = data["package_imports_occurence"]
		self.test_directory_dependencies = data["test_directory_dependencies"]
		self.main_packages = data["main_packages"]
		self.main_package_deps = data["main_package_deps"]
		return True