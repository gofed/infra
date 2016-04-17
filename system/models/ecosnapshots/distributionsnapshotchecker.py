from infra.system.core.factory.actfactory import ActFactory
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT
from gofed_lib.eco.capturer import EcoCapturer
from infra.system.core.acts.types import ActFailedError
from infra.system.core.functions.types import FunctionFailedError
from gofed_lib.helpers import GolangRpm
from gofed_lib.utils import BLUE, YELLOW, ENDC, WHITE
from gofed_lib.distributionsnapshot import DistributionSnapshot
import json
import logging

#
# TODO(jchaloup):
# - introduce event logger for logging all progress messages instead of printing them
#

class DistributionSnapshotChecker(object):
	"""Checkout the ecosystem for new builds
	1. get the latest snapshot of each requested distribution
	2. get the current shapshot for each requested distribution
	3. compare both snapshots
	4. scan new rpms
	"""

	def __init__(self, koji_client, pkgdb_client):
		"""

		:param koji_client: Koji client
		:type  koji_client: KojiClient or FakeKojiClient
		:param pkgdb_client: PkgDB client
		:type  pkgdb_client: PkgDBClient or FakePkgDBClient
		"""
		self.koji_client = koji_client
		self.pkgdb_client = pkgdb_client

		self.artefactreaderact = ActFactory().bake("artefact-reader")
		self.artefactwriteract = ActFactory().bake("artefact-writer")
		self.scanbuildact = ActFactory().bake("scan-distribution-build")

		self._failed = {}
		self._scanned = {}

	def _scanRpms(self, snapshot):
		"""Scan rpms captured in snapshot

		:param snapshot: distribution snapshot or difference
		:type  snapshot: DistributionSnapshot
		"""
		distribution = snapshot.distribution()
		key = "%s:%s" % (distribution["product"], distribution["version"])
		self._failed[key] = []
		self._scanned[key] = 0

		print "%sScanning %s %s ...%s" % (BLUE, distribution["product"], distribution["version"], ENDC)
		total = len(snapshot.json()["builds"])
		index = 1
		for package in snapshot.json()["builds"]:
			# scan devel and unit-tests only
			rpms = filter(lambda l: GolangRpm(package["build"], l).provideSourceCode(), package["rpms"])

			if rpms == []:
				continue

			data = {
				"product": distribution["product"],
				"distribution": distribution["version"],
				"build": {
					"name": package["build"],
					"rpms": map(lambda l: {"name": l}, rpms)
				}
			}

			print "%sScanning %s ... [%s/%s]%s" % (WHITE, package["build"], index, total, ENDC)
			index = index + 1
			try:
				self.scanbuildact.call(data)
			except ActFailedError as e:
				logging.error(e)
				self._failed[key].append(package)
				continue
			except FunctionFailedError as e:
				logging.error(e)
				self._failed[key].append(package)
				continue

			self._scanned[key] = self._scanned[key] + 1

		print "%sscanned %s, failed %s%s" % (YELLOW, self._scanned[key], len(self._failed[key]), ENDC)
		print ""

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
			print distribution

			try:
				data = self.artefactreaderact.call({
					"artefact": ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT,
					"distribution": distribution
				})
			except ActFailedError:
				continue

			distro_packages = distro_packages + DistributionSnapshot().read(data).builds().keys()

		known_packages = list(set(distro_packages + custom_packages))

		# capture the current distribution snapshot
		capturer = EcoCapturer(self.koji_client, self.pkgdb_client)

		snapshots = capturer.captureLatest(distributions, known_packages, blacklist).snapshots()

		for snapshot in snapshots:
			new_snapshot = snapshots[snapshot]["snapshot"]

			# get the latest distribution snapshot
			latest_snapshot = {}

			if not full_check:
				try:
					data = self.artefactreaderact.call({
						"artefact": ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT,
						"distribution": snapshots[snapshot]["distribution"]
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
				key = "%s:%s" % (distribution["product"], distribution["version"])
				if self._failed[key] > 0:
					write = False

			if write:
				data = new_snapshot.json()
				data["artefact"] = ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT
				try:
					self.artefactwriteract.call(data)
				except ActFactory:
					logging.error("Unable to store snapshot for %s:%s" % (distribution["product"], distribution["version"]))

