import logging
logger = logging.getLogger("distribution_packages_fetcher")

import time
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT
from infra.system.core.acts.types import ActFailedError
from infra.system.core.functions.types import FunctionFailedError
from infra.system.core.factory.actfactory import ActFactory
from gofed_lib.distribution.distributionsnapshot import DistributionSnapshot
from gofed_lib.utils import BLUE, YELLOW, ENDC, WHITE

from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS

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
			product = distribution.product()
			version = distribution.version()
			if product not in collections:
				raise ValueError("Product '%s' unknown" % product)
			if version not in collections[ product ]:
				raise ValueError("Version '%s' unknown" % version)

		# get list of packages to scan
		for distribution in distributions:
			product = distribution.product()
			version = distribution.version()
			dist_tag = collections[product][version]["dist_tag"]

			logger.info("%sScanning %s %s ...%s" % (YELLOW, product, version, ENDC))
			try:
				data = self.artefactreaderact.call({
					"artefact": ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT,
					"distribution": distribution.json()
				})
			except ActFailedError:
				logger.error("Distribution snapshot for '%s' not found" % distribution)
				continue

			builds = DistributionSnapshot().read(data).builds()
			for build in builds:
				if builds[build]["build_ts"] >= since:
					logger.info("%sScanning %s ...%s" % (BLUE, build, ENDC))
					# get package's items info artefact
					try:
						items_info = self.artefactreaderact.call({
							"artefact": ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS,
							"product": distribution.product(),
							"distribution": dist_tag,
							"package": build
						})
					except ActFailedError as e:
						items_info = None

					# if items_info artefact for package is found, take the build timestamp
					# of the youngest covered build
					if items_info == None:
						start_ts = since
					else:
						start_ts = 0
						for coverage in items_info["coverage"]:
							start_ts = max(coverage["end"], start_ts)
						# end is always > 0
						start_ts = start_ts - 1

					try:
						self.scan_act.call({
							"package": build,
							"product": distribution.product(),
							"distribution": dist_tag,
							"start_timestamp": start_ts,
							"end_timestamp": to
						})
					except ActFailedError as e:
						logger.error("%s: %s" (build, e))
						continue

		return self
