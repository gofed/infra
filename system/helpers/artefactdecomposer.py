# NOTES:
# - create more strategies of decomposition
# - distribution prefix strategy: decompose artefacts based on /usr/share/gocode/src/ipprefix prefix
#

from infra.system.artefacts import artefacts

STRATEGY_DISTRIBUTION_PREFIX = 1

DISTRO_PREFIX = "usr/share/gocode/src/"
DISTRO_PREFIX_LEN = len(DISTRO_PREFIX)
DISTRO_DOC_PREFIX = "usr/share/doc/"

class ArtefactDecomposer:
	"""

	"""

	def __init__(self, ipparser, strategy = STRATEGY_DISTRIBUTION_PREFIX):
		self.ipparser = ipparser
		self.classes = {}

	def _artefact_golang_project_distribution_exported_api_distribution_prefix_strategy(self, artefact):
		pkg_classes = {}
		for package in artefact["packages"]:
			# the only supported prefix atm is /usr/share/gocode/src
			pkg = package["package"]

			# if the package is prefixed with /usr/share/doc/, filter it out
			# TODO(jchaloup): for doc create a new property in the artefact
			if pkg.startswith(DISTRO_DOC_PREFIX):
				continue

			if not pkg.startswith(DISTRO_PREFIX):
				raise ValueError("Package %s does not start with %s" % (pkg, DISTRO_PREFIX))

			path = pkg[DISTRO_PREFIX_LEN:]
			key = self.ipparser.parse(path).prefix()
			package["package"] = path

			try:
				pkg_classes[key].append(package)
			except KeyError:
				pkg_classes[key] = [package]

		data = []
		for prefix in pkg_classes:
			data.append({
				"ipprefix": prefix,
				"data": pkg_classes[prefix]
			})

		new_artefact = {
			"artefact": artefact["artefact"],
			"packages": data,
			"product": artefact["product"],
			"build": artefact["build"],
			# commit not always right
			"commit": artefact["commit"],
			"distribution": artefact["distribution"],
			"rpm": artefact["rpm"],
		}

		if "project" in artefact:
			new_artefact["project"] = artefact["project"]

		return new_artefact

	def _artefact_golang_project_distribution_packages_distribution_prefix_strategy(self, artefact):
		"""
		TODO(jchaloup):
			[  ] - extend spec file with more commit macros for each ipprefix
		"""
		# empty data => nothing to decompose
		if artefact["data"] == {}:
			return artefact

		# decompose list of packages
		pkg_classes = {}
		for package in artefact["data"]["packages"]:
			# if the package is prefixed with /usr/share/doc/, filter it out
			# TODO(jchaloup): for doc create a new property in the artefact
			if package.startswith(DISTRO_DOC_PREFIX):
				continue

			# the only supported prefix atm is /usr/share/gocode/src
			if not package.startswith(DISTRO_PREFIX):
				raise ValueError("Package %s does not start with %s" % (package, DISTRO_PREFIX))

			path = package[DISTRO_PREFIX_LEN:]
			key = self.ipparser.parse(path).prefix()

			try:
				pkg_classes[key].append(path)
			except KeyError:
				pkg_classes[key] = [path]

		# decompose dependencies
		dep_classes = {}
		for dep in artefact["data"]["dependencies"]:
			package = dep["package"]

			# if the package is prefixed with /usr/share/doc/, filter it out
			# TODO(jchaloup): for doc create a new property in the artefact
			if package.startswith(DISTRO_DOC_PREFIX):
				continue

			if not package.startswith(DISTRO_PREFIX):
				raise ValueError("Package %s does not start with %s" % (package, DISTRO_PREFIX))

			path = package[DISTRO_PREFIX_LEN:]
			key = self.ipparser.parse(path).prefix()
			dep["package"] = path

			try:
				dep_classes[key].append(dep)
			except KeyError:
				dep_classes[key] = [dep]

		# main packages
		main_classes = {}
		for main in artefact["data"]["main"]:
			filename = main["filename"]

			# if the package is prefixed with /usr/share/doc/, filter it out
			# TODO(jchaloup): for doc create a new property in the artefact
			if filename.startswith(DISTRO_DOC_PREFIX):
				continue

			if not filename.startswith(DISTRO_PREFIX):
				raise ValueError("Main %s does not start with %s" % (filename, DISTRO_PREFIX))

			path = filename[DISTRO_PREFIX_LEN:]
			key = self.ipparser.parse(path).prefix()

			main["filename"] = path
			try:
				main_classes[key].append(main)
			except KeyError:
				main_classes[key] = [main]

		# tests
		test_classes = {}
		for test in artefact["data"]["tests"]:
			package = test["test"]

			# if the package is prefixed with /usr/share/doc/, filter it out
			# TODO(jchaloup): for doc create a new property in the artefact
			if package.startswith(DISTRO_DOC_PREFIX):
				continue

			if not package.startswith(DISTRO_PREFIX):
				raise ValueError("Package %s does not start with %s" % (package, DISTRO_PREFIX))

			path = package[DISTRO_PREFIX_LEN:]
			key = self.ipparser.parse(path).prefix()

			test["test"] = path
			try:
				test_classes[key].append(test)
			except KeyError:
				test_classes[key] = [test]

		# nonempty list of classes must be the same for all parts
		classes_len = filter(lambda l: l > 0, [len(pkg_classes.keys()), len(dep_classes.keys()), len(main_classes.keys()), len(test_classes.keys())])
		if max(classes_len) != min(classes_len):
			raise ValueError("Not every data belongs to the same set of classes")

		# collect common classes
		classes_keys = filter(lambda l: l != [], [pkg_classes.keys(), dep_classes.keys(), main_classes.keys(), test_classes.keys()])
		if classes_keys == []:
			raise ValueError("No prefix class detected")

		comm_classes = set(classes_keys[0])
		for keys in classes_keys:
			if  len(comm_classes) != len(set(keys) & comm_classes):
				raise ValueError("Not every data belongs to the same set of classes")

		# decompose
		data = []
		for prefix in comm_classes:
			data.append({
				"ipprefix": prefix,
				"packages": pkg_classes[prefix] if prefix in pkg_classes else [],
				"dependencies": dep_classes[prefix] if prefix in dep_classes else [],
				"main": main_classes[prefix] if prefix in main_classes else [],
				"tests": test_classes[prefix] if prefix in test_classes else []
			})

		new_artefact = {
			"artefact": artefact["artefact"],
			"data": data,
			"product": artefact["product"],
			"build": artefact["build"],
			# commit not always right
			"commit": artefact["commit"],
			"distribution": artefact["distribution"],
			"rpm": artefact["rpm"],
		}

		if "project" in artefact:
			new_artefact["project"] = artefact["project"],

		return new_artefact

	def decomposeArtefact(self, artefact):
		if artefact["artefact"] == artefacts.ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES:
			return self._artefact_golang_project_distribution_packages_distribution_prefix_strategy(artefact)
		if artefact["artefact"] == artefacts.ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API:
			return self._artefact_golang_project_distribution_exported_api_distribution_prefix_strategy(artefact)

		raise ValueError("artefact '%s' unrecognized" % artefact["artefact"])

	def decompose(self, artefacts):
		o_artefacts = []
		for artefact in artefacts:
			o_artefacts = o_artefacts + self.decomposeArtefact(artefact)
		return o_artefacts
