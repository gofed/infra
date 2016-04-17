import time
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT
from infra.system.core.acts.types import ActFailedError
from infra.system.core.functions.types import FunctionFailedError
from infra.system.core.factory.actfactory import ActFactory
from gofed_lib.distributionsnapshot import DistributionSnapshot
from gofed_lib.utils import BLUE, YELLOW, ENDC, WHITE

class DistributionBuildsFetcher(object):

	def __init__(self, pkgdb_client):
		self.pkgdb_client = pkgdb_client

		self.artefactreaderact = ActFactory().bake("artefact-reader")
		self.artefactwriteract = ActFactory().bake("artefact-writer")
		self.scan_act = ActFactory().bake("scan-distribution-package")

	def fetch(self, distributions, since = 0, to = int(time.time() + 86400)):
		"""Collect list of builds since a given date for each package
		whose builds is younger than since.

		:param distributions: list of distributions to fetch builds from
		:type  distributions: [distribution]
		:param since: since timestamp from which to collect new builds
		:type  since: int
		:param to: timestamp to which collect new builds
		:type  to: int
		"""

		collections = self.pkgdb_client.getCollections()
		for distribution in distributions:
			if distribution["product"] not in collections:
				logging.error("Product '%s' unknown" % distribution["product"])
				return
			if distribution["version"] not in collections[ distribution["product"] ]:
				logging.error("Version '%s' unknown" % distribution["version"])
				return

		# get list of packages to scan
		for distribution in distributions:
			dist_tag = collections[distribution["product"]][distribution["version"]]["dist_tag"]

			print "%sScanning %s %s ...%s" % (BLUE, distribution["product"], distribution["version"], ENDC)
			try:
				data = self.artefactreaderact.call({
					"artefact": ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT,
					"distribution": distribution
				})
			except ActFailedError:
				continue

			builds = DistributionSnapshot().read(data).builds()
			for build in builds:
				if builds[build]["build_ts"] >= since:
					print "%sScanning %s ...%s" % (BLUE, build, ENDC)
					try:
						self.scan_act.call({
							"package": build,
							"product": distribution["product"],
							"distribution": dist_tag,
							"start_timestamp": since,
							"end_timestamp": to
						})
					except ActFailedError as e:
						logging.error("%s: %s" (build, e))
						continue
