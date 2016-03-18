import json

class Graph(object):

	def __init__(self, nodes, edges):
		self._nodes = nodes
		self._edges = edges

	def nodes(self):
		return self._nodes

	def edges(self):
		return self._edges

	def __str__(self):
		return json.dumps({
			"nodes": self._nodes,
			"edges": self._edges
		})
