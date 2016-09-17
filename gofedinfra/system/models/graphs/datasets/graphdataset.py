class GraphDataset(object):
	"""Encapsulation of graph dataset
	"""
	def __init__(self, nodes = [], edges = {}, alphabet = [], parents = {}, labels = {}):
		self._nodes = nodes
		self._edges = edges
		self._alphabet = alphabet
		self._parents = parents
		self._labels = labels

	def nodes(self):
		return self._nodes

	def edges(self):
		return self._edges

	def alphabet(self):
		return self._alphabet

	def parents(self):
		return self._parents

	def labels(self):
		return self._labels

	def getLabelEdges(self, categories = ["devel"]):
		edges = {}
		for category in categories:
			for key in self._labels[category]:
				for label in self._labels[category][key]:
					u, v = label
					try:
						edges[u].append(v)
					except KeyError:
						edges[u] = [v]

		for u in edges:
			edges[u] = list(set(edges[u]))

		return edges
