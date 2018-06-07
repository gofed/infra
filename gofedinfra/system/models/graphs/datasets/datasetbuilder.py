from .graphdataset import GraphDataset
import os

class DatasetBuilder(object):

	def __init__(self, with_main = False, with_tests = False):
		self._requirements = []
		self._dataset = GraphDataset()

		self.with_main = with_main
		self.with_tests = with_tests

	def dataset(self):
		return self._dataset

	def addArtefact(self, artefact, node_name = ("-", "-")):
		self._requirements.append(
			self._extractRequirements(artefact, node_name)
		)

		return self

	def addDistributionArtefact(self, artefact):
		if "golang-project-distribution-packages" == artefact["artefact"]:
			self._requirements.append(
				self._extractProjectDistributionPackagesRequirements(artefact, (artefact["build"], artefact["rpm"]))
			)
			return self

		raise ValueError("Artefact is not valid packages artefact: %s" % artefact)

	def build(self):
		self._dataset = self._buildGraph()

		return self

	def _extractRequirements(self, artefact, node_name):
		if "golang-project-distribution-packages" == artefact["artefact"]:
			return self._extractProjectDistributionPackagesRequirements(artefact, node_name)
		if "golang-project-packages" == artefact["artefact"]:
			return self._extractProjectPackagesRequirements(artefact, node_name)

		raise ValueError("Artefact is not valid packages artefact: %s" % artefact)

	def _prefixPackage(self, prefix, package):
		if package == ".":
			return prefix
		return "%s/%s" % (prefix, package)

	def _extractProjectPackagesRequirements(self, artefact, node_name):
		"""
		:param artefact: golang-project-*-packages artefact
		:type  artefact: json
		"""
		# collect vertices and edges
		vertices = {}
		edges = {}

		vertices[node_name] = {}
		edges[node_name] = {}

		# vertices
		vertices[node_name]["devel"] = []
		for package in artefact["data"]["packages"]:
			vertices[node_name]["devel"].append(self._prefixPackage(artefact["ipprefix"], package))

		# edges
		edges[node_name]["devel"] = []
		for package in artefact["data"]["dependencies"]:
			edges[node_name]["devel"] = edges[node_name]["devel"] + map(lambda l: (package, l), artefact["data"]["dependencies"][package])

		# main packages
		vertices[node_name]["main"] = []
		edges[node_name]["main"] = []
		for main in artefact["data"]["main"]:
			# dirname from filename says in which package the dependencies are required/imported
			pkg = os.path.dirname(main)
			vertices[node_name]["main"].append(pkg)
			edges[node_name]["main"] = edges[node_name]["main"] + map(lambda l: (pkg, l), artefact["data"]["main"][main])
		# one directory can have multiple filename import the same package
		edges[node_name]["main"] = list(set(edges[node_name]["main"]))

		# unit-tests
		vertices[node_name]["tests"] = []
		edges[node_name]["tests"] = []
		for package in artefact["data"]["tests"]:
			vertices[node_name]["tests"].append(package)
			edges[node_name]["tests"] = edges[node_name]["tests"] + map(lambda l: (package, l), artefact["data"]["tests"][package])

		return (vertices, edges)

	def _extractProjectDistributionPackagesRequirements(self, artefact, node_name):
		"""Build edges and vertices for each iprefix of a given rpm (generate edges no matter of the destination node exists)

		:param artefact: golang-project-*-packages artefact
		:type  artefact: json
		"""
		# collect vertices and edges
		vertices = {}
		edges = {}
		vertices[node_name] = {}
		edges[node_name] = {}

		for prefix_unit in artefact["data"]:
			# vertices
			vertices[node_name]["devel"] = []
			for package in prefix_unit["packages"]:
				vertices[node_name]["devel"].append(package)

			# edges
			edges[node_name]["devel"] = []
			for dependencies in prefix_unit["dependencies"]:
				edges[node_name]["devel"] = edges[node_name]["devel"] + map(lambda l: (dependencies["package"], l["name"]), dependencies["dependencies"])

			# main packages
			vertices[node_name]["main"] = []
			edges[node_name]["main"] = []
			for main in prefix_unit["main"]:
				# dirname from filename says in which package the dependencies are required/imported
				pkg = os.path.dirname(main["filename"])
				vertices[node_name]["main"].append(pkg)
				edges[node_name]["main"] = edges[node_name]["main"] + map(lambda l: (pkg, l),  main["dependencies"])
			# one directory can have multiple filename import the same package
			edges[node_name]["main"] = list(set(edges[node_name]["main"]))

			# unit-tests
			vertices[node_name]["tests"] = []
			edges[node_name]["tests"] = []
			for test in prefix_unit["tests"]:
				vertices[node_name]["tests"].append(test["test"])
				edges[node_name]["tests"] = edges[node_name]["tests"] + map(lambda l: (test["test"], l),  test["dependencies"])

		return (vertices, edges)

	def _buildGraph(self):
		"""Join or individual iprefix graphs into one graph

		"""
		# TODO(jchaloup): extend nodes on a level of files?
		vertices = []	# [rpm]
		edges = []	# [(rpm,rpm)]
		alphabet = []	# [package]
		parents = {}	# alphabet -> vertices
		labels = {}	# label can contain (package, package) each with a package not in alphabet
		labels["devel"] = {}	# (rpm,rpm | "") -> label
		labels["main"] = {}	# (rpm,rpm | "") -> label
		labels["tests"] = {}	# (rpm,rpm | "") -> label

		# nodes: rpms				// list of rpms provided by specified packages
		# edge: (rpm, rpm)			// list of used rpms
		# alphabet: [package]			// list of golang packages defined by all rpms
		# parents: package -> rpm mapping	// list of used packages (each package belongs to one and only one rpm)
		# label: ([(package, package), ...], [(package, package), ...], [(package, package), ...])
		#         devel                      main                       unit-test
		# This way I get a graph from which I can run analysis on level of rpms and level of golang packages.
		# Each analysis will preprocess the graph and get what it needs:
		# - rpm level: just picks nodes and edges as it is (this will not give a list of missing packages)
		# - golang package level: from labels collect edges, from parents collect a list of missing packages, from alphabet get a list of all packages
		#
		# TODO:
		# - how to detect missing packages on rpm-level?
		categories = ["devel"]
		if self.with_main:
			categories.append("main")
		if self.with_tests:
			categories.append("tests")

		for v, _ in self._requirements:
			for key in v:
				(build, rpm) = key
				vertices.append(rpm)
				# symbols
				for category in categories:
					alphabet = alphabet + v[key][category]

					# parents
					for l in v[key][category]:
						parents[l] = {"build": build, "rpm": rpm}

		for _, e in self._requirements:
			for key in e:
				(build, rpm) = key
				for category in categories:
					for (a, b) in e[key][category]:
						# edges
						try:
							target_rpm = parents[b]["rpm"]
							edges.append((rpm, target_rpm))
						except KeyError:
							#print "Missing node: %s" % b
							target_rpm = ""

						# labels
						try:
							labels[category][(rpm,target_rpm)].append((a,b))
						except KeyError:
							labels[category][(rpm,target_rpm)] = [(a,b)]

		# make the list of edges unique
		edges = list(set(edges))
		# make alphabet unique
		alphabet = list(set(alphabet))

		return GraphDataset(vertices, edges, alphabet, parents, labels)
