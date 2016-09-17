import unittest
from .basicdependencyanalysis import BasicDependencyAnalysis
from gofedlib.graphs.graphutils import GraphUtils, Graph

class BasicDependencyAnalysisTest(unittest.TestCase):

	def test(self):

		g = Graph()

		expected = {
			"cycles": set([]),
			"roots": set([]),
			"leaves": set([])
		}

		a = BasicDependencyAnalysis(g)
		a.analyse()
		self.assertEqual(a.results(), expected)
