from .graphdataset import GraphDataset
import os

class DatasetBuilder(object):

	def __init__(self):
		self._requirements = []
		self._dataset = GraphDataset()

	def dataset(self):
		return self._dataset

	def addArtefact(self, artefact):
		self._requirements.append(
			self._extractRequirements(artefact)
		)

		return self

	def build(self):
		self._dataset = self._buildGraph()

		return self

	def _extractRequirements(self, artefact):
		if artefact["artefact"] == "golang-project-distribution-packages":
			return self._extractProjectDistributionRequirements(artefact)
		if artefact["artefact"] == "golang-project-packages":
			return self._extractProjectPackagesRequirements(artefact)

		raise ValueError("Artefact '%s' not supported" % artefact["artefact"])

	def _extractProjectPackagesRequirements(self, artefact):
		"""
		:param artefact: golang-project-*-packages artefact
		:type  artefact: json
		"""
		# collect vertices and edges
		vertices = {}
		edges = {}

		prefix_unit = "-"
		vertices[prefix_unit] = {}
		edges[prefix_unit] = {}

		# vertices
		vertices[prefix_unit]["devel"] = []
		for package in artefact["data"]["packages"]:
			vertices[prefix_unit]["devel"].append("%s/%s" % (artefact["ipprefix"], package))

		# edges
		edges[prefix_unit]["devel"] = []
		for dependencies in artefact["data"]["dependencies"]:
			edges[prefix_unit]["devel"] = edges[prefix_unit]["devel"] + map(lambda l: ("%s/%s" % (artefact["ipprefix"], dependencies["package"]), l["name"]), dependencies["dependencies"])

		# main packages
		vertices[prefix_unit]["main"] = []
		edges[prefix_unit]["main"] = []
		for main in artefact["data"]["main"]:
			# dirname from filename says in which package the dependencies are required/imported
			pkg = os.path.dirname(main["filename"])
			vertices[prefix_unit]["main"].append("%s/%s" % (artefact["ipprefix"], pkg))
			edges[prefix_unit]["main"] = edges[prefix_unit]["main"] + map(lambda l: ("%s/%s" % (artefact["ipprefix"], pkg), l),  main["dependencies"])
		# one directory can have multiple filename import the same package
		edges[prefix_unit]["main"] = list(set(edges[prefix_unit]["main"]))

		# unit-tests
		vertices[prefix_unit]["tests"] = []
		edges[prefix_unit]["tests"] = []
		for test in artefact["data"]["tests"]:
			vertices[prefix_unit]["tests"].append("%s/%s" % (artefact["ipprefix"], test["test"]))
			edges[prefix_unit]["tests"] = edges[prefix_unit]["tests"] + map(lambda l: ("%s/%s" % (artefact["ipprefix"], test["test"]), l),  test["dependencies"])

		return (vertices, edges)

	def _extractProjectDistributionPackagesRequirements(self, artefact):
		"""
		:param artefact: golang-project-*-packages artefact
		:type  artefact: json
		"""
		# collect vertices and edges
		vertices = {}
		edges = {}
		for rpm in artefact:
			vertices[rpm] = {}
			edges[rpm] = {}
			for prefix_unit in artefact[rpm]["data"]:
				# vertices
				vertices[rpm]["devel"] = []
				for package in prefix_unit["packages"]:
					vertices[rpm]["devel"].append(package)

				# edges
				edges[rpm]["devel"] = []
				for dependencies in prefix_unit["dependencies"]:
					edges[rpm]["devel"] = edges[rpm]["devel"] + map(lambda l: (dependencies["package"], l["name"]), dependencies["dependencies"])

				# main packages
				vertices[rpm]["main"] = []
				edges[rpm]["main"] = []
				for main in prefix_unit["main"]:
					# dirname from filename says in which package the dependencies are required/imported
					pkg = os.path.dirname(main["filename"])
					vertices[rpm]["main"].append(pkg)
					edges[rpm]["main"] = edges[rpm]["main"] + map(lambda l: (pkg, l),  main["dependencies"])
				# one directory can have multiple filename import the same package
				edges[rpm]["main"] = list(set(edges[rpm]["main"]))

				# unit-tests
				vertices[rpm]["tests"] = []
				edges[rpm]["tests"] = []
				for test in prefix_unit["tests"]:
					vertices[rpm]["tests"].append(test["test"])
					edges[rpm]["tests"] = edges[rpm]["tests"] + map(lambda l: (test["test"], l),  test["dependencies"])

		return (vertices, edges)

	def _buildGraph(self):
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

		for v, _ in self._requirements:
			for rpm in v:
				vertices.append(rpm)
				# symbols
				alphabet = alphabet + v[rpm]["devel"] + v[rpm]["main"] + v[rpm]["tests"]
				# parents
				for l in v[rpm]["main"] + v[rpm]["tests"] + v[rpm]["devel"]:
					parents[l] = rpm

		for _, e in self._requirements:
			for rpm in e:
				for category in ["devel", "main", "tests"]:
					for (a, b) in e[rpm][category]:
						# edges
						try:
							target_rpm = parents[b]
							edges.append((rpm, target_rpm))
						except KeyError:
							#print "Missing node: %s" % b
							target_rpm = ""

						# labels
						try:
							labels[category][(rpm,target_rpm)].append((a,b))
						except KeyError:
							labels[category][(rpm,target_rpm)] = [(a,b)]

		category = "devel"
		for label in labels[category]:
			if len(labels[category][label]) != len(list(set(labels[category][label]))):
				print (label, len(labels[category][label]), len(list(set(labels[category][label]))))
				print labels[category][label]

		# make the list of edges unique
		edges = list(set(edges))
		# make alphabet unique
		alphabet = list(set(alphabet))

		return GraphDataset(vertices, edges, alphabet, parents, labels)

