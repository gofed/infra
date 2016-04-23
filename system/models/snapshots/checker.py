#
# Snapshot checker
# - check if a given snaphost is covered in a given distribution
#
# Algorithm:
# 1. map each (ipprefix, commit) pair to (provider prefix, commit) pair
# 2. map each ipprefix to (package, spec commit) pair
# 3. get commit date for both pairs from 1. and 2.
# 4. compare dates (up-to-date, outdated, newer)
# 5. check if all ips in ipprefix class are actually covered by package
#
# To check a given Go project provides a set of packages, use artefacts.
# Spec's list of provided packages does not have to be up-to-date.
# It is up to lint to report missing/superfluous packages.
#
# If artefact for a given commit is not found, scan the commit.
# Store the artefact after. Don't update repo cache and info artefacts.
# I will get dangling commits. However, the commit gets picked eventually.
# Some commits can get lost forever (e.g. git push --force). For that reason,
# etcd is not a good storage as it can not provide a list of values.
# Maybe, it could be hacked? Open upstream PR for that?
#
# To cover step 2., I need ipprefix to package name mapping.
# At the moment, only import_path macro is parsed. Spec/package can provide
# multiple ipprefixes. Still, some of the defined macro does not have to be used
# at all. At the same time, ipprefix macros can be missing. So the only realiable
# way to get a list of ipprefixes is to scan every rpm shipping source codes.
# The ip2pkg mapping artefact is already generated. It just need to be extended
# with additional values. Thus, for a given build scan srpm and all devel rpms
# and for each found ipprefix generate on ip2pkg mapping artefact.
# The second part is to extend each ip2pkg artefact with commit. In general,
# there is only one iprefix for all commits in a given project. However,
# some projects may change its prefix while living in a repository. There are
# two situation that have happend so far:
# - project was moved from one repository to another (code.google.com to github.com)
#   while keeping its content. Thus changing its prefix
# - project changes its prefix while kept in the same repository (code.google.com to
#   golang.org/x)
# At the same time the commit is needed to keep ipprefix and commit tied together.
#
# One rpm can provide multiple ipprefix of different commits. For that reason
# I need a way to specify which commit belongs to which ipprefix.
# Thus new macro is introduced:
# 	%global ipprefix2commit "ipprefix:commit,ipprefix:commit"
# I.e., comma separated list of ipprefix:commit pairs.
# If a given prefix is not listed in the macro, %commit is used as default.
#
# At the same time ip2pkg artefact will provide rpm in which the ipprefix is so one
# can check if a given list of packages from ipprefix class is provided by the rpm.
#
# One package can provide two ipprefixe each with its own provider prefix.
# For that reason new macro is introduced:
#	%global ipprefix2provider "ipprefix:providerprefix,ipprefix:providerprefix"
#
# This macro is future feature macro and will implemented when needed.
#

from gofed_lib.go.importpath.parserbuilder import ImportPathParserBuilder
from gofed_lib.providers.providerbuilder import ProviderBuilder
from infra.system.core.factory.actfactory import ActFactory
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_IPPREFIX_TO_RPM,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
	ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT
)
from infra.system.core.acts.types import ActFailedError
import logging
from gofed_lib.utils import RED, GREEN, BLUE, WHITE, ENDC


class SnapshotChecker(object):

	def __init__(self):
		self.ipparser = ImportPathParserBuilder().buildWithLocalMapping()
		self.artefactreaderact = ActFactory().bake("artefact-reader")
		self.commitreaderact = ActFactory().bake("scan-upstream-repository")

		self._project_provider = ProviderBuilder().buildUpstreamWithLocalMapping()

	def _getCommitDate(self, repository, commit):
		try: 
			artefact = self.commitreaderact.call({
				"repository": repository,
				"commit": commit
			})
		except ValueError as e:
			logging.error(e)
			return {}

		return artefact[ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT][commit]

	def _comparePackages(self, package, upstream_commit, distro_commit):
		if upstream_commit["cdate"] == distro_commit["cdate"]:
			return "%s%s is up-to-date%s" % (GREEN, package, ENDC)
		elif upstream_commit["cdate"] < distro_commit["cdate"]:
			return "%s%s is newer in distribution%s" % (BLUE, package, ENDC)
		elif upstream_commit["cdate"] > distro_commit["cdate"]:
			return "%s%s is outdated in distribution%s" % (RED, package, ENDC)

	def _checkPackageCoverage(self, product, distribution, build, rpm, ipprefix, packages):
		data = {
			"artefact": ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
			"product": product,
			"distribution": distribution,
			"build": build,
			"rpm": rpm
		}
		artefact = self.artefactreaderact.call(data)

		# get list of defined packages
		for ipprefix_class in artefact["data"]:
			if ipprefix_class["ipprefix"] == ipprefix:
				# All packages covered?
				return list(set(packages) - set(ipprefix_class["packages"]))

	def check(self, snapshot, product, distribution):
		"""Check if a given snapshot is covered in a distribution
		:param snapshot: project snapshot
		:type  snapshot: Snapshot
		:param distribution: OS distribution, e.g. f23, f25, rawhide, centos7, ...
		:type  distribution: string
		"""

		packages = snapshot.packages()

		ipprefixes = {}
		providers = {}
		rpms = {}
		upstream = {}
		not_recognized = []
		for package in packages:
			try:
				self.ipparser.parse(package)
			except ValueError:
				not_recognized.append(package)
				continue

			ipprefix = self.ipparser.prefix()
			try:
				ipprefixes[ipprefix].append(package)
			except KeyError:
				ipprefixes[ipprefix] = [package]

			# store ipprefix commit (assuming all packages with the same prefix has the same commit)
			upstream[ipprefix] = packages[package]

			# iprefix -> provider prefix
			providers[ipprefix] = self._project_provider.parse(ipprefix).signature()

			# ipprefix -> rpm
			data = {
				"artefact": ARTEFACT_GOLANG_IPPREFIX_TO_RPM,
				"distribution": "rawhide",
				"product": "Fedora",
				"ipprefix": ipprefix
			}
			# if ipprefix2rpm artefact does not exist => report it and continue, no fallback
			# TODO(jchaloup): FF: fallback to generic mapping if ipprefix to pkg name
			# and report that "maybe" the ipprefix is provided by this package
			try:
				rpms[ipprefix] = self.artefactreaderact.call(data)
			except ActFailedError as e:
				logging.error("Unable to get mapping for %s" % package)
				pass

		for ipprefix in ipprefixes:
			if ipprefix not in providers:
				print "%sUnable to find provider for '%s' ipprefix%s" % (WHITE, ipprefix, ENDC)
				continue

			if ipprefix not in rpms:
				print "%sUnable to find ipprefix2rpm mapping '%s' ipprefix%s" % (WHITE, ipprefix, ENDC)
				continue

			upstream_commit = self._getCommitDate(providers[ipprefix], upstream[ipprefix])
			distro_commit = self._getCommitDate(providers[ipprefix], rpms[ipprefix]["commit"])

			if upstream_commit == {}:
				logging.error("Unable to retrieve commit info for %s %s" % (package, packages[package]))
				continue

			if distro_commit == {}:
				logging.error("Unable to retrieve commit info for %s %s" % (package, rpms[package]["commit"]))
				continue

			# compare commits
			comparison = self._comparePackages(ipprefix, upstream_commit, distro_commit)

			# check if packages in ipprefix class are covered in distribution
			not_covered = self._checkPackageCoverage(product, distribution, rpms[ipprefix]["build"], rpms[ipprefix]["rpm"], ipprefix, ipprefixes[ipprefix])

			if not_covered != []:
				print "%s: %snot covered: %s%s" % (comparison, RED, not_covered, ENDC)
			else:
				print comparison
