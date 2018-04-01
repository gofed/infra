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
import logging
logger = logging.getLogger("distribution_latest_builds_dataset_builder")

from gofedlib.distribution.helpers import Rpm
import json

from .datasetbuilder import DatasetBuilder
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT
from gofedlib.distribution.distributionsnapshot import DistributionSnapshot
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES

from infra.system.workers import Worker, WorkerException
from infra.system.plugins.simplefilestorage.storagereader import StorageReader

class DistributionLatestBuildGraphDataset:

	def __init__(self, dry_run=False):
		"""The graph can be built from all packages or from selected.
		The decision is up to user of the class.

		:param distribution: OS distribution
		:type  distribution: string
		:param packages: list of packages in question
		:type  packages: [string]
		"""
		# TODO(jchaloup):
		# - inject the product together with buildsystem client
		# TODO(jchaloup):
		# - inject the act and replace it with datasource instead
		#   so the artefact/data can be picked from more sources

	def build(self, distribution):
		"""Build dataset for a given list of buildes
		"""
		# get latets rpms from the latest distribution snapshot
		try:
			artefact = StorageReader().retrieve({
				"artefact": ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT,
				"distribution": distribution.json()
			})
		except KeyError:
			raise KeyError("Distribution snapshot for '%s' not found" % distribution)

		counter = 0
		builder = DatasetBuilder()

		builds = DistributionSnapshot().read(data).builds()
		builds_total = len(builds)
		builds_counter = 0
		for pkg in builds:
			builds_counter = builds_counter + 1
			logger.info("%s/%s Processing %s" % (builds_counter, builds_total, builds[pkg]["build"]))

			# get artefact
			data = {
				"product": distribution.product(),
				"distribution": distribution.version(),
				"build": {
					"name": builds[pkg]["build"],
					"rpms": map(lambda l: {"name": l}, builds[pkg]["rpms"])
				}
			}

			for rpm in builds[pkg]["rpms"]:
				artefact_key = {
					"artefact": ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
					"product": distribution.product(),
					"distribution": distribution.version(),
					"build": builds[pkg]["build"],
					"rpm": rpm,
				}

				try:
					artefact = StorageReader().retrieve(artefact_key)
				except KeyError:
					Worker("scandistributionbuild").setPayload({
						"product": product,
						"distribution": version,
						"build": {
							"name": builds[pkg]["build"],
							"rpms": builds[pkg]["rpms"],
						}
					}).do()

				try:
					artefact = StorageReader().retrieve(artefact_key)
				except KeyError as e:
					logger.error(e)
					continue

				builder.addDistributionArtefact(artefact)

		return builder.build().dataset()
