from gofed_lib.graphs.graphutils import Graph
from gofed_lib.graphs.graphutils import GraphUtils

# nodes = rpms
LEVEL_RPM = 1
# nodes = golang projects
LEVEL_GOLANG_PACKAGES = 2

class DatasetDependencyGraphBuilder(object):

	def __init__(self):
		self._missing_packages = []

	def _buildRpmLevelGraph(self, dataset):
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

		return Graph(nodes, edges)

	def _buildGolangPackageLevelGraph(self, dataset):
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

		# TODO(jchaloup): integrate parent mapping as well so one can join packages from the same rpm
		return Graph(nodes, edges)

	def missingPackages(self):
		return self._missing_packages

	def build(self, dataset, level = LEVEL_RPM):
		"""From a given dataset build a graph
		:param dataset: dataset that a graph can be built from
		:type  dataset: json
		:param level: level of graph construction
		:type  level: LEVEL_RPM | LEVEL_GOLANG_PACKAGES
		"""
		if level == LEVEL_RPM:
			return self._buildRpmLevelGraph(dataset)
		if level == LEVEL_GOLANG_PACKAGES:
			return self._buildGolangPackageLevelGraph(dataset)
