import logging
logger = logging.getLogger("distribution_packages_fetcher")

import time
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT
# from infra.system.core.factory.actfactory import ActFactory
# from infra.system.core.factory.fakeactfactory import FakeActFactory
from gofedlib.distribution.distributionsnapshot import DistributionSnapshot
from gofedlib.utils import BLUE, YELLOW, ENDC, WHITE

from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS
from infra.system.workers import Worker, WorkerException
from infra.system.plugins.simplefilestorage.storagereader import StorageReader

class DistributionBuildsFetcher(object):

	def __init__(self, pkgdb_client, dry_run=False):
		self._pkgdb_client = pkgdb_client

		# TODO(jchaloup): make the dry work again
		# if dry_run:
		# 	act_factory = FakeActFactory()
		# else:
		# 	act_factory = ActFactory()

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

		collections = self._pkgdb_client.getCollections()
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
				data = StorageReader().retrieve({
					"artefact": ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT,
					"distribution": distribution.json(),
				})
			except KeyError:
				logger.error("Distribution snapshot for '%s' not found" % distribution)
				continue

			builds = DistributionSnapshot().read(data).builds()
			for build in builds:
				if builds[build]["build_ts"] >= since:
					logger.info("%sScanning %s ...%s" % (BLUE, build, ENDC))
					try:
						Worker("scandistributionpackage").setPayload({
							"product": distribution.product(),
							"distribution": dist_tag,
							"package": build,
							"from_ts": since,
							"to_ts": to,
						}).do()
					except WorkerException as e:
						logger.error("%s: %s" (build, e))
						continue

		return self
