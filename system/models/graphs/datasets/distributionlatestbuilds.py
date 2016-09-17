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
from infra.system.core.factory.actfactory import ActFactory
from infra.system.core.factory.fakeactfactory import FakeActFactory
import json

from infra.system.core.functions.types import FunctionFailedError
from infra.system.core.acts.types import ActFailedError
from .datasetbuilder import DatasetBuilder
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT
from gofedlib.distribution.distributionsnapshot import DistributionSnapshot
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES

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
		if dry_run:
			act_factory = FakeActFactory()
		else:
			act_factory = ActFactory()

		self.scan_distribution_build_act = act_factory.bake("scan-distribution-build")
		self.artefactreaderact = act_factory.bake("artefact-reader")

	def build(self, distribution):
		"""Build dataset for a given list of buildes
		"""
		# get latets rpms from the latest distribution snapshot
		try:
			data = self.artefactreaderact.call({
				"artefact": ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT,
				"distribution": distribution.json()
			})
		except ActFailedError:
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

			try:
				artefacts = self.scan_distribution_build_act.call(data)
			except FunctionFailedError as e:
				logger.error(e)
				continue

			for rpm in artefacts[ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES]:
				builder.addDistributionArtefact(artefacts[ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES][rpm])

		return builder.build().dataset()

