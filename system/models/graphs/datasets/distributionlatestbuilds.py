# Get a list/set of golang-project-distribution-packages artefact of the latest builds
# in a distribution and transform them to a data suitable for graph builder

# Specification:
# - nodes: distribution rpms
# - edges: (a, b) = rpm a depends on rpm b
# 
# - support for multigraphs:
#   - as one rpm (a) can import more packages from the same rpm (b), there can be more edges between two nodes in general
#   - when constructing a dependency graph, all multiedges get merge into one
#
# - support for multilayer edges:
#   - dependency graph is constructed over devel subpackage. However, it makes sense to contruc the graph over main packages and unit-tests.
#     Main packages only import packages. Unit-test can do both but usually they only import packages.

# Steps:
# - get artefacts from core layer
# - build a graph over the artefacts
# - return the graph

from gofed_lib.kojiclient import FakeKojiClient, KojiClient
from gofed_lib.helpers import Rpm
from system.core.factory.actfactory import ActFactory
import os
import json
import logging

from infra.system.core.functions.types import FunctionFailedError
from .graphdataset import GraphDataset

class DistributionLatestBuildGraphDataset:

	def __init__(self, distribution, packages):
		"""The graph can be built from all packages or from selected.
		The decision is up to user of the class.

		:param distribution: OS distribution
		:type  distribution: string
		:param packages: list of packages in question
		:type  packages: [string]
		"""
		# TODO(jchaloup):
		# - inject the product together with buildsystem client
		self.product = "Fedora"
		self.distribution = distribution
		self.packages = packages
		# TODO(jchaloup):
		# - inject the client so the class can be used with Brew and CentOS as well
		self.client = FakeKojiClient()
		# TODO(jchaloup):
		# - inject the act and replace it with datasource instead
		#   so the artefact/data can be picked from more sources
		self.act = ActFactory().bake("scan-distribution-build")

	def _extractRequirements(self, artefact):
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

	def _buildGraph(self, requirements):
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

		for v, _ in requirements:
			for rpm in v:
				vertices.append(rpm)
				# symbols
				alphabet = alphabet + v[rpm]["devel"] + v[rpm]["main"] + v[rpm]["tests"]
				# parents
				for l in v[rpm]["main"] + v[rpm]["tests"] + v[rpm]["devel"]:
					parents[l] = rpm

		for _, e in requirements:
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

	def build(self):
		"""Build dataset for a given list of buildes
		"""
		# TODO(jchaloup): specify json schema for a dataset
		# get a list of latest rpms for selected packages
		counter = 0
		requirements = []
		for pkg in self.packages:
			if pkg in ["golang-github-aws-aws-sdk-go", "golang-googlecode-google-api-go-client", "golang-googlecode-google-api-client"]:
				continue

			try:
				data = self.client.getLatestRPMS("rawhide", pkg)
			except ValueError as e:
				logging.error("ValueError: %s" % e)
				continue
			except KeyError as e:
				logging.error("KeyError: %s" % e)
				continue

			rpms = []
			for rpm in data["rpms"]:
				rpm_name = Rpm(data["name"], rpm["name"]).name()
				#if not rpm_name.endswith("devel"): # and not rpm["name"].endswith("unit-test"):
				#	continue

				rpms.append({"name": rpm["name"]})

			# get artefact
			data = {
				"product": self.product,
				"distribution": self.distribution,
				"build": {
					"name": data["name"],
					"rpms": rpms
				}
			}

			try:
				artefacts = self.act.call(data)
			except FunctionFailedError as e:
				logging.error(e)
				continue

			requirements.append(self._extractRequirements(artefacts["packages"]))
			
			if counter == 40:
				break

			counter = counter + 1

		return self._buildGraph(requirements)

