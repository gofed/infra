from metaprocessor import MetaProcessor
import os
from system.helpers.utils import getScriptDir, runCommand
import logging
import json

CONFIG_SOURCE_CODE_DIRECTORY = "source_code_directory"
CONFIG_SKIPPED_DIRECTORIES = "directories_to_skip"
DATA_PROJECT = "project"
DATA_COMMIT = "commit"
DATA_IPPREFIX = "ipprefix"
ARTEFACT_GOLANG_PROJECT_PACKAGES = "golang-project-packages"
ARTEFACT_GOLANG_PROJECT_EXPORTED_API = "golang-project-exported-api"

class GoSymbolExtractor(MetaProcessor):
	"""
	Input: 
	 - directory to parse
	 - directories to skip
	Input(json):
	 {
	 "source_code_directory": "...",
	 "skipped_directories": "...,...,..."
	 }
	Output:
	 - exported API
	 - imported packages
	 - occurence of imported packages
	 - test directories
	 - main packages
	 - is Godeps directory present (an others)?
	Output(json):
	 {
	 ""
	 }
	Configuration:
	 - verbose mode
	 - log directory
	 To make the class config indepenent, all flags
	 are passed via class methods.
	"""


	def __init__(self):
		"""Setting implicit flags"""
		self.verbose = False
		self.skip_errors = False
		self.imports_only = False

		"""set implicit output"""
		self.symbols = []
                self.symbols_position = {}
                # list of packages imported for each project's package
                self.package_imports = {}
                # list of packages imported in entire project
                self.imported_packages = []
                # occurences of imported paths in packages
                self.package_imports_occurence = {}
                self.test_directories = []
                # main packages
                self.main_packages = []
                # Godeps directory is present
                self.godeps_on = False 
		# project
		self.project = ""
		# commit
		self.commit = ""

		"""set implicit states"""
		self.input_validated = False
		self.directory = ""

	def setVerbose(self):
		self.verbose = True

	def setSkipErrors(self):
		self.skip_errors = True

	def _validateInput(self, data):
		if CONFIG_SOURCE_CODE_DIRECTORY not in data:
			logging.error("Input data missing source_code_directory")
			return False

		self.input_validated = True
		return True

	def setData(self, data):
		self.input_validated = False
		self.data = data

		if not self._validateInput(data):
			return False

		# set directory with source codes to parse
		self.directory = data[CONFIG_SOURCE_CODE_DIRECTORY]

		# optional, set a list of directories to be skipped during parsing
		if CONFIG_SKIPPED_DIRECTORIES in data:
			self.noGodeps = data[CONFIG_SKIPPED_DIRECTORIES]

		# optional, project, commit, ipprefix
		if DATA_PROJECT in data:
			self.project = data[DATA_PROJECT]

		if DATA_COMMIT in data:
			self.commit = data[DATA_COMMIT]

		if DATA_IPPREFIX in data:
			self.ipprefix = data[DATA_IPPREFIX]

		return True

	def getData(self):
		data = []

		data.append(self._generateGolangProjectPackagesArtefact())
		data.append(self._generateGolangProjectExportedAPI())

		return data

	def _generateGolangProjectPackagesArtefact(self):
		data = {}

		# set artefact
		data["artefact"] = ARTEFACT_GOLANG_PROJECT_PACKAGES

		# project credentials
		data["project"] = self.project
		data["commit"] = self.commit
		data["ipprefix"] = self.ipprefix

		# package imports
		package_imports = {}
		for key in self.package_imports:
			path = str(key.split(":")[0])
			arr = sorted(map(lambda i: str(i), self.package_imports[key]))
			package_imports[path] = ",".join(arr)

		data["dependencies"] = package_imports

		# list of defined packages (defined package has at least one exported symbol)
		data["packages"] = ",".join(map(lambda i: str(i.split(":")[0]), self.symbols.keys()))

		# list of tests
		data["tests"] = ",".join(map(lambda i: str(i), self.test_directories))

		# files with 'package main'
		data["main"] = ",".join(map(lambda i: str(i), self.main_packages))

		# Godeps directory located
		data["godeps_found"] = self.godeps_on

		return data

	def _generateGolangProjectExportedAPI(self):
		data = {}

		# set artefact
		data["artefact"] = ARTEFACT_GOLANG_PROJECT_EXPORTED_API

		# project credentials
		data["project"] = self.project
		data["commit"] = self.commit

		packages = []
		for key in self.symbols:
			package = {}

			# full package name (location of a package without ipprefix)
			path = str(key.split(":")[0])
			package["package"] = path

			# data types
			for type in self.symbols[key]["types"]:
				print type

			print package
			break

		return data

	def execute(self):
		if not self.input_validated:
			logging.error("Input data are not validated")
			return False

		return self._extract()

	def _getGoFiles(self, directory):
		go_dirs = []
		for dirName, subdirList, fileList in os.walk(directory):
			# skip all directories with no file
			if fileList == []:
				continue

			go_files = []
			for fname in fileList:
				# find any *.go file
				if fname.endswith(".go"):
					go_files.append(fname)

			# skipp all directories with no *.go file
			if go_files == []:
				continue

			relative_path = os.path.relpath(dirName, directory)
			go_dirs.append({
				'dir': relative_path,
				'files': go_files,
			})

		return go_dirs

	def _getGoSymbols(self, path, imports_only=False):
		script_dir = getScriptDir(__file__) + "/."
		options = ""
		if imports_only:
			options = "-imports"

		so, se, rc = runCommand("%s/parseGo %s %s" % (script_dir, options, path))
		if rc != 0:
			return (1, se)

		return (0, so)

	def _mergeGoSymbols(self, jsons = []):
		"""
		Exported symbols for a given package does not have any prefix.
		So I can drop all import paths that are file specific and merge
		all symbols.
		Assuming all files in the given package has mutual exclusive symbols.
		"""
		# <siXy> imports are per file, exports are per package
		# on the highest level we have: pkgname, types, funcs, vars, imports.

		symbols = {}
		symbols["types"] = []
		symbols["funcs"] = []
		symbols["vars"]  = []
		for file_json in jsons:
			symbols["types"] += file_json["types"]
			symbols["funcs"] += file_json["funcs"]
			symbols["vars"]  += file_json["vars"]

		return symbols

	def _extract(self):
		"""

		"""
		bname = os.path.basename(self.directory)
		go_packages = {}
		ip_packages = {}
		test_directories = []
		ip_used = []
		package_imports = {}
		main_packages = []

		for dir_info in self._getGoFiles(self.directory):
			if dir_info["dir"].startswith("Godeps"):
				self.godeps_on = True

			#if sufix == ".":
			#	sufix = bname
			pkg_name = ""
			prefix = ""
			jsons = {}
			if self.noGodeps != []:
				skip = False
				path_components = dir_info['dir'].split("/")
				for nodir in self.noGodeps:
					parts = nodir.split(":")
					name = parts[0]
					# empty means all elements
					max_depth = len(path_components)
					if len(parts) == 2 and parts[1].isdigit():
						max_depth = int(parts[1])

					if name in path_components[0:max_depth]:
						skip = True
						break
				if skip:
					continue

			for go_file in dir_info['files']:

				if self.verbose:
					logging.warning("Scanning %s..." % ("%s/%s" % (dir_info['dir'], go_file)))

				go_file_json = {}
				err, output = self._getGoSymbols("%s/%s/%s" % 
					(self.directory, dir_info['dir'], go_file), self.imports_only)
				if err != 0:
					if self.skip_errors:
						continue
					else:
						logging.error("Error parsing %s: %s" % ("%s/%s" % (dir_info['dir'], go_file), output))
						return False
				else:
					#print go_file
					go_file_json = json.loads(output)

				pname = go_file_json["pkgname"]

				for path in go_file_json["imports"]:
					# filter out all import paths starting with ./
					if path["path"].startswith("./"):
						continue

					# filter out all .. import paths
					if path["path"] == "..":
						continue

					# file_pkg_pair:
					# 1: path to a directory defining a package
					# 2: package NAME actually used in 'package NAME'
					if dir_info['dir'] == ".":
						file_pkg_pair = "%s:%s" % (go_file, pname)
					else:
						file_pkg_pair = "%s/%s:%s" % (dir_info['dir'], go_file, pname)

					if path["path"] not in self.package_imports_occurence:
						self.package_imports_occurence[str(path["path"])] = [str(file_pkg_pair)]
					else:
						self.package_imports_occurence[str(path["path"])].append(str(file_pkg_pair))

					if path["path"] in ip_used:
						continue

					ip_used.append(path["path"])

				# don't check test files, read their import paths only
				if go_file.endswith("_test.go"):
					test_directories.append(dir_info['dir'])
					continue

				# skip all main packages
				if pname == "main":
					if dir_info['dir'] == ".":
						main_packages.append(go_file,)
					else:
						main_packages.append("%s/%s" % (dir_info['dir'], go_file))
					continue

				# all files in a directory must define the same package
				if (pkg_name != "" and pkg_name != pname):
					err_msg = "directory %s contains definition of more packages, i.e. %s" % (dir_info['dir'], pname)
					logging.error("%s" % err_msg)

					if self.skip_errors:
						continue

					return False

				# convention is to have dirname = packagename, but not necesary
				if pname != os.path.basename(dir_info['dir']):
					logging.warning("directory %s != package name %s" % (dir_info['dir'], pname))

				pkg_name = pname

				# build can contain two different prefixes
				# but with the same package name.
				prefix = dir_info["dir"] + ":" + pkg_name
				i_paths = map(lambda i: i["path"], go_file_json["imports"])
				if prefix not in jsons:
					jsons[prefix] = [go_file_json]
					package_imports[prefix] = i_paths
				else:
					jsons[prefix].append(go_file_json)
					package_imports[prefix] = package_imports[prefix] + i_paths

			#print dir_info["dir"]
			#print dir_info['files']
			#print "#%s#" % pkg_name
			if prefix in jsons:
				go_packages[prefix] = self._mergeGoSymbols(jsons[prefix])
				ip_packages[prefix] = dir_info["dir"]
				package_imports[prefix] = list(set(package_imports[prefix]))

		self.symbols = go_packages
		self.symbols_position = ip_packages
		self.package_imports = package_imports
		self.imported_packages = ip_used
		self.test_directories = list(set(test_directories))
		self.main_packages = main_packages

		return True

