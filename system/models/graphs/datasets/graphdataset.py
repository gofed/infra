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
