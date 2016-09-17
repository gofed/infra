from gofedlib.graphs.graphutils import GraphUtils

class BasicDependencyAnalysis(object):

	def __init__(self, graph):
		self._graph = graph

		self._cycles = set([])
		self._roots = set([])
		self._leaves = set([])

	def _getCyclicDependencies(self, graph):
		return GraphUtils.getSCCs(graph)

	def _getRootNodes(self, graph):
		return GraphUtils.getRootNodes(graph)

	def _getLeafNodes(self, graph):
		return GraphUtils.getLeafNodes(graph)

	def results(self):
		return {
			"cycles": self._cycles,
			"roots": self._roots,
			"leaves": self._leaves
		}

	def analyse(self):
		"""Carry basic analysis of dependency graph (independent of graph level)
		- missing packages
		- cyclic dependencies
		- root & leaf nodes
		"""
		cycles = self._getCyclicDependencies(self._graph)
		for cycle in cycles:
			if len(cycle) > 1:
				self._cycles.add(cycle)

		self._roots = self._getRootNodes(self._graph)

		self._leaves = self._getLeafNodes(self._graph)

		return self
