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
import json
import logging

from infra.system.core.functions.types import FunctionFailedError
from .datasetbuilder import DatasetBuilder

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

	def build(self):
		"""Build dataset for a given list of buildes
		"""
		# TODO(jchaloup): specify json schema for a dataset
		# get a list of latest rpms for selected packages
		counter = 0

		builder = DatasetBuilder()
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

			builder.addArtefact(artefacts["packages"])
			
			#if counter == 60:
			#	break

			counter = counter + 1

		return builder.build().dataset()

