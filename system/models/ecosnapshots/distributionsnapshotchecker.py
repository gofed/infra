import logging
logger = logging.getLogger("distribution_snapshot_capturer")

from infra.system.core.factory.actfactory import ActFactory
from infra.system.core.factory.fakeactfactory import FakeActFactory
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT
from gofedlib.distribution.eco.capturer import EcoCapturer
from infra.system.core.acts.types import ActFailedError
from infra.system.core.functions.types import FunctionFailedError
from gofedlib.distribution.helpers import GolangRpm
from gofedlib.utils import BLUE, YELLOW, ENDC, WHITE
from gofedlib.distribution.distributionsnapshot import DistributionSnapshot
import json

class DistributionSnapshotChecker(object):
	"""Checkout the ecosystem for new builds
	1. get the latest snapshot of each requested distribution
	2. get the current shapshot for each requested distribution
	3. compare both snapshots
	4. scan new rpms
	"""

	def __init__(self, koji_client, pkgdb_client, dry_run=False):
		"""

		:param koji_client: Koji client
		:type  koji_client: KojiClient or FakeKojiClient
		:param pkgdb_client: PkgDB client
		:type  pkgdb_client: PkgDBClient or FakePkgDBClient
		"""
		self._koji_client = koji_client
		self._pkgdb_client = pkgdb_client
		if dry_run:
			act_factory = FakeActFactory()
		else:
			act_factory = ActFactory()

		self._artefactreaderact = act_factory.bake("artefact-reader")
		self._artefactwriteract = act_factory.bake("artefact-writer")
		self._scanbuildact = act_factory.bake("scan-distribution-build")

		self._failed = {}
		self._scanned = {}

	def _scanRpms(self, snapshot):
		"""Scan rpms captured in snapshot

		:param snapshot: distribution snapshot or difference
		:type  snapshot: DistributionSnapshot
		"""
		distribution = snapshot.distribution()
		product = distribution.product()
		version = distribution.version()
		key = "%s:%s" % (product, version)
		self._failed[key] = []
		self._scanned[key] = 0

		logger.info("%sScanning %s ...%s" % (BLUE, distribution, ENDC))
		total = len(snapshot.json()["builds"])
		index = 1
		for package in snapshot.json()["builds"]:
			# scan devel and unit-tests only
			rpms = filter(lambda l: GolangRpm(package["build"], l).provideSourceCode(), package["rpms"])

			if rpms == []:
				continue

			data = {
				"product": product,
				"distribution": version,
				"build": {
					"name": package["build"],
					"rpms": map(lambda l: {"name": l}, rpms)
				}
			}

			logger.info("%s%s/%s scanning %s ... %s" % (WHITE, index, total, package["build"], ENDC))
			index = index + 1
			try:
				self._scanbuildact.call(data)
			except ActFailedError as e:
				logger.error(e)
				self._failed[key].append(package)
				continue
			except FunctionFailedError as e:
				logger.error(e)
				self._failed[key].append(package)
				continue

			self._scanned[key] = self._scanned[key] + 1

		logger.info("%sscanned %s, failed %s%s" % (YELLOW, self._scanned[key], len(self._failed[key]), ENDC))

	def _distroKey(self, distribution):
		return "%s:%s" % (distribution["product"], distribution["version"])

	def check(self, distributions, custom_packages, blacklist = [], skip_failed = True, full_check = False):
		"""

		:param distributions: list of distributions, each item as {"product": ..., "version": ...}
		:type  distributions: [{}]
		:param custom_packages: list of golang packages not prefixed with golang-*
		:type  custom_packages: [string]
		:param skip_failed: even if any rpm scan fails, store the latest snapshot, default True
		:type  skip_failed: boolean
		:param full_scan: don't check the current snapshot and scan all rpms in the latest snapshot
		:type  full_scan: boolean
		"""
		# read all latest snapshots and get a list of all packages across them
		distro_packages = []
		for distribution in distributions:
			try:
				data = self._artefactreaderact.call({
					"artefact": ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT,
					"distribution": distribution.json()
				})
			except ActFailedError:
				continue

			distro_packages = distro_packages + DistributionSnapshot().read(data).builds().keys()

		known_packages = list(set(distro_packages + custom_packages))

		# capture the current distribution snapshot
		capturer = EcoCapturer(self._koji_client, self._pkgdb_client)

		snapshots = capturer.captureLatest(distributions, known_packages, blacklist).snapshots()

		for snapshot in snapshots:
			new_snapshot = snapshots[snapshot]["snapshot"]

			# get the latest distribution snapshot
			latest_snapshot = {}

			if not full_check:
				try:
					data = self._artefactreaderact.call({
						"artefact": ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT,
						"distribution": snapshots[snapshot]["distribution"].json()
					})
					latest_snapshot = DistributionSnapshot().read(data)
				except ActFailedError:
					# TODO(jchaloup): catch additional exception once extended
					pass

			# scan new rpms
			# the latest snapshot not found => no comparison
			if latest_snapshot == {}:
				diff_snapshot = new_snapshot
			else:
				diff_snapshot = new_snapshot.compare(latest_snapshot)

			self._scanRpms(diff_snapshot)

			# Set the latest snapshot
			write = True
			if not skip_failed:
				distribution = snapshots[snapshot]["distribution"]
				key = "%s:%s" % (distribution.product(), distribution.version())
				if len(self._failed[key]) > 0:
					write = False

			if write:
				data = new_snapshot.json()
				data["artefact"] = ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT

				try:
					self._artefactwriteract.call(data)
				except ActFactory:
					logger.error("Unable to store snapshot for %s:%s" % (distribution.product(), distribution.version()))

