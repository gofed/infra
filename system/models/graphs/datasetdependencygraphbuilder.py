from gofed_lib.graphs.graphutils import Graph
from gofed_lib.graphs.graphutils import GraphUtils
from gofed_lib.distribution.helpers import Build

# nodes = rpms
LEVEL_RPM = 1
# nodes = golang projects
LEVEL_GOLANG_PACKAGES = 2

class DatasetDependencyGraphBuilder(object):

	def __init__(self):
		self._missing_packages = []

	def _buildRpmLevelGraph(self, dataset, root_package = ""):
		"""
		:param root_package: distribution package
		"""
		# get nodes and edges
		nodes = dataset.nodes()
		edges = dataset.edges()

		# get missing packages
		labels = dataset.labels()

		missing = []
		for category in labels:
			# TODO(jchaloup): make distinction among devel, main and tests
			for edge in labels[category]:
				a, b = edge
				if b == "":
					missing = missing + list(set(map(lambda (a,b): b, labels[category][edge])))

		self._missing_packages = list(set(missing))

		# convert edges to adjacent list
		edges = GraphUtils.edges2adjacentList(edges)

		# find the corresponding rpm
		if root_package != "":
			root_rpm = ""
			for rpm_sig in dataset.parents().values():
				if Build(rpm_sig["build"]).name() == root_package:
					root_rpm = rpm_sig["rpm"]
					break

			if root_rpm == "":
				raise KeyError("Root package '%s' not found" % root_package)

			return GraphUtils.truncateGraph(Graph(nodes, edges), [root_rpm])

		return Graph(nodes, edges)

	def _buildGolangPackageLevelGraph(self, dataset, root_package):
		"""
		:param root_package: go project package
		"""
		# get nodes
		nodes = dataset.alphabet()
		# get edges from labels
		labels = dataset.labels()

		missing = []
		edges = []
		for category in labels:
			for edge in labels[category]:
				a, b = edge
				if b == "":
					missing = missing + list(set(map(lambda (a,b): b, labels[category][edge])))
				else:
					edges = edges + labels[category][edge]

		self._missing_packages = list(set(missing))

		# mixing all categories we can get repeating edges
		edges = list(set(edges))

		# convert edges to adjacent list
		edges = GraphUtils.edges2adjacentList(edges)

		# find the corresponding rpm
		if root_package != "":
			return GraphUtils.truncateGraph(Graph(nodes, edges), [root_package])

		# TODO(jchaloup): integrate parent mapping as well so one can join packages from the same rpm
		return Graph(nodes, edges)

	def missingPackages(self):
		return self._missing_packages

	def build(self, dataset, level = LEVEL_RPM, root_node = ""):
		"""From a given dataset build a graph
		:param dataset: dataset that a graph can be built from
		:type  dataset: json
		:param level: level of graph construction
		:type  level: LEVEL_RPM | LEVEL_GOLANG_PACKAGES
		"""
		if level == LEVEL_RPM:
			return self._buildRpmLevelGraph(dataset, root_node)
		if level == LEVEL_GOLANG_PACKAGES:
			return self._buildGolangPackageLevelGraph(dataset, root_node)
