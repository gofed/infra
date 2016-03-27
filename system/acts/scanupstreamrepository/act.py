#
# Extraction of artefacts from an upstream repository
#
# Upstream repositories in question: github.com, bitbucket.com, code.google.com, golang.google.org
#
# Expected input of the act is repository and date interval. Usually, the interval will a few days long.
# Sometimes a moth. It is not expected to provide entire list of commits for a given repository often.
# For that case, the repository will be scaned by interval after an interval in arbitrary order.
#
# Expected use cases:
# - get a list of commits in a given month
# - get a list of commits that are around a given date (as date interval with required date inside of it)
#
# In order to support the expected use cases, a coverage date intervals are introduced.
# Each set of artefacts corresponds to a date interval. Usually, there will be some commits
# already stored in a storage. Request for date interval can hit subset of commits not yet stored.
# For that reason, merge mechanism for two set of commits is required.
#
# To support retrival of list of commits in a given date interval without reading every commit
# for a given repository, cache with (commit, commit date) is introduced. The cache will
# support coverage of date intervals as well.
#
# Expected workflow:
# 1. a given repository is not stored => extract artefact for a given interval
# 2. a given repository is stored
# 2.1 a given date interval is not covered
# 2.2 a given date interval is covered
#
# 1. This is the simplest case. In general, a list of artefacts (one for each commit) is stored.
# Some commits may not be stored (error, policy). Thus a list of stored commits is constructed
# and the date interval is decomposed the way the missing commits has to be extracted from a repository
# again if a commit fits into requested date interval not yet covered.
# At the end, repository-info artefact is stored. It provides a list of commits currently stored.
# At the same time it provides a coverage (list of data intervals that are covered)
#
# 2. Again, the list of extracted commits is stored and a list of stored commits retrieved.
# If a commit already exists in a storage, it is replaced with exactly the same copy.
# Once extracted, the current repository-info artefact gets retrieved.
# Both new and retrieved info artefacts get merged together.
# Once merged, new cache gets generated. Again, new and the currect cache (retrived from a storage)
# get merged.
# Once merged, repository info gets stored. If it fails to store, exception is raised.
# As the last, cache gets store. If it fails, exceptions is raised.
#
# 2.2 If a given data interval is stored, the cache and info artefacts get retrieved.
# Once filtered (to a given data interval), acts returns the data.
#
# Can data stay in inconsistent state?
# Commits get stored. Those are atomic operation. If a given commits does not get stored,
# it is put into a list of non-stored commits.
# Repository info artefact gets updated based on the non-stored commits list.
# If the info artefact does not get stored, some commits can be unreferrenced.
# Still, it is ok. At worst, the list of commits gets extracted again.
# If the cache does not get stored, a list of commits and repository info gets
# extracted again.
#
# Steps to be taken if date interval not covered (cache is missing or interval not cached)
# 1. extract the data interval
# 2. retrieve the current info and cache artefacts
# 3. merge both pairs of caches and infos
# 4. stored info first, then cache
#
# Again, why do I need the cache?
# Cache collect a list of commits with their corresponding commit dates.
# Cache may live independent of repository-info artefact. Repository info
# can get removed (by accident or by admin). For that reason, cache is not
# replacement for repository-info.
# At the same time, cache can referrence non-existing commit which was
# removed from a storage (by accident or by admin). The cache does not guarantee
# a referreced commit is stored. It only guarantees a commit with a given commit date
# existed in a time when the cache was generated.

from infra.system.core.meta.metaact import MetaAct
from infra.system.resources.specifier import ResourceSpecifier
from infra.system.resources import types
from infra.system.helpers.utils import getScriptDir
from infra.system.artefacts.artefacts import (
	ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS,
	ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO,
	ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT
)

from gofed_lib.utils import dateToTimestamp
from infra.system.helpers.cacheintervalmerger import CacheIntervalMerger, CacheIntervalBreaker
from gofed_lib.utils import intervalCovered
from infra.system.core.acts.types import ActDataError

class ScanUpstreamRepositoryAct(MetaAct):

	def __init__(self):
		MetaAct.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__)
		)

		self.repository_info = {}
		self.repository_commits = {}

	def setData(self, data):
		"""Validation and data pre-processing"""
		if not self._validateInput(data):
			return False

		self.repository = data["repository"]

		self.start_date = ""
		if 'start_date' in data:
			self.start_date = data["start_date"]

		self.end_date = ""
		if 'end_date' in data:
			self.end_date = data["end_date"]

		return True

	def getData(self):
		"""Validation and data post-processing"""
		return {
			"info": self.repository_info,
			"commits": self.repository_commits
		}

	def _extractRepositoryData(self):
		# no cache => extract the data
		resource = ResourceSpecifier().generateUpstreamRepository(
			self.repository["provider"],
			self.repository["username"],
			self.repository["project"]
		)

		data = {
			"repository": self.repository,
			"resource": resource
		}

		if self.start_date != "":
			data["start_date"] = self.start_date

		if self.end_date != "":
			data["end_date"] = self.end_date

		return self.ff.bake("repositorydataextractor").call(data)

	def _processRepositoryData(self, repository_artefacts):
		"""Store all commit artefacts, return list of stored commits
		and repository_info artefact.

		"""
		stored_commits = []
		not_stored_commits = []
		info_artefact = {}
		for artefact in repository_artefacts:
			if artefact["artefact"] == ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT:
				# even if a commit does not get stored, index it
				self.repository_commits[artefact["commit"]] = artefact

				# TODO(jchaloup): just for testing purposes, make it configurable
				# store artefact
				if not self.ff.bake("etcdstoragewriter").call(artefact):
					not_stored_commits.append({
						"c": artefact["commit"],
						"d": artefact["cdate"]
					})
					logging.error("Unable to store artefact: %s" % json.dumps(artefact))
					continue

				stored_commits.append({
					"c": artefact["commit"],
					"d": artefact["cdate"]
				})

			elif artefact["artefact"] == ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO:
				info_artefact = artefact

		return (info_artefact, stored_commits, not_stored_commits)

	def _generateNewCache(self, commits, coverage):
		# construct cache
		return {
			"artefact": ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS,
			"repository": self.repository,
			"coverage": coverage,
			"commits": commits
		}

	def _mergeCacheCommits(self, commits1, commits2):
		commits = {}

		for commit in commits1:
			commits[commit["c"]] = commit

		for commit in commits2:
			commits[commit["c"]] = commit

		return commits.values()

	def _mergeCaches(self, cache1, cache2):
		cache = {
			"artefact": ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS,
			"repository": cache2["repository"]
		}

		# merge cache intervals
		cache["coverage"] = CacheIntervalMerger().merge(cache1["coverage"], cache2["coverage"])

		# merge commits
		cache["commits"] = self._mergeCacheCommits(cache1["commits"], cache2["commits"])

		return cache

	def mergeRepositoryInfoArtefacts(self, info1, info2):
		return {
			"artefact": ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS,
			"repository": info2["repository"],
			"commits": list(set(info1["commits"]) | set(info2["commits"])),
			"coverage": CacheIntervalMerger().merge(info1["coverage"], info2["coverage"])
		}

	def _storeCache(self, cache):
		if not self.ff.bake("etcdstoragewriter").call(cache):
			# TODO(jchaloup): this needs to be handled if configured to run
			logging.error("Unable to store cache")

	def generateCacheFromArtefacts(self, repository_info):
		"""Generate list of (commit, commit date) pairs from repository info artefact.
		If any read from a storage fails, the cache can be incomplete.
		Let's use what we get and give the cache another chance to get reconstructed in another scan.

		:param repository_info: repository info artefact
		:type  repository_info: artefact
		"""
		cache_commits = []
		for commit in repository_info["commits"]:
			# construct a storage request for each commit
			data = {
				"artefact": ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT,
				"repository": repository_info["repository"],
				"commit": commit
			}

			# retrieve commit date for each commit
			commit_found, commit_data = self.ff.bake("etcdstoragereader").call(data)
			if commit_found:
				cache_commits.append({
					"c": commit_data["commit"],
					"d": commit_data["cdate"]
				})

		return {
			"artefact": ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS,
			"repository": repository_info["repository"],
			"coverage": repository_info["coverage"],
			"commits": cache_commits
		}

	def execute(self):
		"""Impementation of concrete data processor"""

		# check storage
		# I can not check for spec file specific macros as I need project
		# to get artefact from a storage. Without the project I can not
		# get artefact from a storage.

		self.repository_info = {}
		self.repository_commits = {}

		# read the current list of commits stored in storage
		# if the youngest commit is younger than end_date, no need to extract data
		# if so, filter out commits older than start_date
		# otherwise extract the missing commits from repository,
		# update the current list of commits and return the relevant sublist
		# with all commits inside the sublist

		# cached?
		data = {
			"artefact": ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS,
			"repository": self.repository
		}

		cache_found, cache = self.ff.bake("etcdstoragereader").call(data)
		# Is the date interval covered?
		if cache_found and self.end_date != "" and self.start_date != "":
			# both ends of date interval are specified
			start_timestamp = dateToTimestamp(self.start_date)
			end_timestamp = dateToTimestamp(self.end_date)

			covered = False
			for coverage in cache["coverage"]:
				print (start_timestamp, end_timestamp)
				print (coverage["start_timestamp"], coverage["end_timestamp"])
				# if date interval not covered => extract
				if intervalCovered(
					(start_timestamp, end_timestamp),
					(coverage["start_timestamp"], coverage["end_timestamp"])
				):
					covered = True
					break

			# data interval is covered, retrieve a list of all relevant commits
			#if covered:
			exit(1)

		# cache not found or data interval not covered

		# extract artefacts
		data = self._extractRepositoryData()
		# store commit artefacts, get a list of stored commits and into artefact
		extracted_info_artefact, stored_commits, not_stored_commits = self._processRepositoryData(data)
		# if some commits are not stored, break the coverate interval into subintervals
		coverage = CacheIntervalBreaker().decompose(stored_commits, not_stored_commits)
		# return unchanged repository info artefact
		self.repository_info = extracted_info_artefact
		# update the artefact to be stored with a list of stored commits
		extracted_info_artefact["coverage"] = coverage
		# update the list of commits being stored
		extracted_info_artefact["commits"] = map(lambda l: l["c"], stored_commits)
		# TODO(jchaloup): check for empty list of commits => we end here

		# generate cache for the extracted data
		extracted_cache = self._generateNewCache(stored_commits, coverage)

		# =============================================
		# if no cache found
		# - info artefact may still exists (cache was removed)
		# - no info artefact
		#
		# if no info artefact => store the created info and cache
		# if info artefact => reconstruct cache from the info by reading all referrenced commit artefact
		# In both cases, i am retrieving info artefact
		# =============================================
		# if cache found:
		# - if info artefact found => compare the cache with a list of commits and coverage of the info.
		#   if there is inconsistency, regenerate cache based on the retrieved repository info artefact.
		# - if info artefact not found => store the extracted info artefact and replace the cache with new cache.
		# In both cases, I am retrieving info artefact
		# =============================================
		# Retranslated:
		# if no info found => replace the current cache with extracted one
		# if info found => sync the current cache with the info and merge both pairs of caches and infos

		# retrieve repository info artefact
		data = {
			"artefact": ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO,
			"repository": self.repository
		}

		info_found, info_artefact = self.ff.bake("etcdstoragereader").call(data)

		# info not found
		if not info_found:
			updated_repository_info = extracted_info_artefact
			updated_cache = extracted_cache
		# info found
		else:
			# merge both infos
			updated_repository_info = self.mergeRepositoryInfoArtefacts(info_artefact, extracted_info_artefact)
			# reconstruct cache from info_artefact
			gen_cache = self.generateCacheFromArtefacts(info_artefact)
			updated_cache = self._mergeCaches(extracted_cache, gen_cache)

		# store both new info and cache
		if not self.ff.bake("etcdstoragewriter").call(updated_repository_info):
			# TODO(jchaloup): if the act is run just to retrieve the artefacts, log the error and continue
			# if it is meant for scanning, raise the exception
			raise ActDataError("Unable to store repository-info: %s" % json.dumps(updated_repository_info))

		# store the cache
		if not self.ff.bake("etcdstoragewriter").call(updated_cache):
			# TODO(jchaloup): based on the configuration raise exception
			# I would like to have the cache saved too
			# Again, for just retrieval of data this is not necassary
			raise ActDataError("Unable to store repository-info: %s" % json.dumps(updated_cache))

		return True
