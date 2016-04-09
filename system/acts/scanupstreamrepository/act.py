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
from infra.system.helpers.itemsetcache.itemsetcache import ItemSetCache
from gofed_lib.utils import intervalCovered
from infra.system.core.acts.types import ActDataError
import logging
import json

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

		self.start_timestamp = ""
		if 'start_timestamp' in data:
			self.start_timestamp = data["start_timestamp"]

		self.end_timestamp = ""
		if 'end_timestamp' in data:
			self.end_timestamp = data["end_timestamp"]

		self.commit = ""
		if 'commit' in data:
			self.commit = data["commit"]

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

		if self.start_timestamp != "":
			data["start_timestamp"] = self.start_timestamp
		elif self.start_date != "":
			data["start_date"] = self.start_date

		if self.end_timestamp != "":
			data["end_timestamp"] = self.end_timestamp
		elif self.end_date != "":
			data["end_date"] = self.end_date

		return self.ff.bake("repositorydataextractor").call(data)

	def _storeRepositoryData(self, repository_commit_artefacts):
		"""Store all commit artefacts, return list of stored commits
		and repository_info artefact.

		"""
		stored_commits = []
		not_stored_commits = []
		for artefact in repository_commit_artefacts:
			# even if a commit does not get stored, index it
			self.repository_commits[artefact["commit"]] = artefact

			# TODO(jchaloup): just for testing purposes, make it configurable
			# store artefact
			if not self.ff.bake("etcdstoragewriter").call(artefact):
				not_stored_commits.append({
					"item": artefact["commit"],
					"point": artefact["cdate"]
				})
				logging.error("Unable to store artefact: %s" % json.dumps(artefact))
				continue

			stored_commits.append({
				"item": artefact["commit"],
				"point": artefact["cdate"]
			})

		return (stored_commits, not_stored_commits)

	def _generateNewCache(self, itemsetcache):
		# construct cache
		return {
			"artefact": ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS,
			"repository": self.repository,
			"coverage": itemsetcache.intervals(),
			"commits": itemsetcache.items()
		}

	def _mergeRepositoryInfoArtefacts(self, info1, info2, coverage):
		# merge branches
		branches1 = {}
		for branch in info1["branches"]:
			branches1[branch["branch"]] = branch["commits"]

		branches2 = {}
		for branch in info2["branches"]:
			branches2[branch["branch"]] = branch["commits"]

		b1_set = set(branches1.keys())
		b2_set = set(branches2.keys())

		branches = {}
		for branch in list(b1_set & b2_set):
			branches[branch] = list(set(branches1[branch]) | set(branches2[branch]))

		for branch in list((b1_set - b2_set)):
			branches[branch] = branches1[branch]

		for branch in list((b2_set - b1_set)):
			branches[branch] = branches2[branch]

		# merged info artefact
		return {
			"artefact": ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS,
			"repository": info2["repository"],
			"branches": branches,
			"coverage": coverage
		}

	def _storeCache(self, cache):
		if not self.ff.bake("etcdstoragewriter").call(cache):
			# TODO(jchaloup): based on the configuration raise exception
			# I would like to have the cache saved too
			# Again, for just retrieval of data this is not necassary
			raise ActDataError("Unable to store cache-repository-info: %s" % json.dumps(cache))

	def _storeInfo(self, info):
		if not self.ff.bake("etcdstoragewriter").call(info):
			# TODO(jchaloup): if the act is run just to retrieve the artefacts, log the error and continue
			# if it is meant for scanning, raise the exception
			raise ActDataError("Unable to store repository-info: %s" % json.dumps(info))

	def _generatePointsFromRepositoryInfoArtefact(self, repository_info):
		"""Generate list of (commit, commit date) pairs from repository info artefact.
		If any read from a storage fails, the cache can be incomplete.
		Let's use what we get and give the cache another chance to get reconstructed in another scan.

		:param repository_info: repository info artefact
		:type  repository_info: artefact
		"""
		items = []
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
				items.append({
					"item": commit_data["commit"],
					"point": commit_data["cdate"]
				})

		return items

	def _retrieveCommitsFromCache(self, cache, start, end):
		# sort commits
		commit_artefacts = {}
		for commit in filter(lambda l: l["point"] >= start and l["point"] <= end, cache["commits"]):
			# construct a storage request for each commit
			data = {
				"artefact": ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT,
				"repository": cache["repository"],
				"commit": commit["item"]
			}

			# retrieve commit date for each commit
			commit_found, commit_data = self.ff.bake("etcdstoragereader").call(data)
			if commit_found:
				commit_artefacts[commit["item"]] = commit_data

		return commit_artefacts

	def _retrieveSingleCommit(self, repository, commit):
		data = {
			"artefact": ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT,
			"repository": repository,
			"commit": commit
		}

		# retrieve commit date for each commit
		commit_found, commit_data = self.ff.bake("etcdstoragereader").call(data)
		if commit_found:
			return commit_data

		# commit not found, extract it
		resource = ResourceSpecifier().generateUpstreamRepository(
			repository["provider"],
			repository["username"],
			repository["project"]
		)

		data = {
			"repository": repository,
			"commit": commit,
			"resource": resource
		}

		return self.ff.bake("repositorydataextractor").call(data)

	def execute(self):
		"""Impementation of concrete data processor"""

		self.repository_info = {}
		self.repository_commits = {}

		# if a self.commit != "" => request only for particular commit
		if self.commit != "":
			self.repository_commits[self.commit] = self._retrieveSingleCommit(self.repository, self.commit)
			return True

		# check storage
		# I can not check for spec file specific macros as I need project
		# to get artefact from a storage. Without the project I can not
		# get artefact from a storage.


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
		if cache_found and (self.end_date != "" or self.end_timestamp != "") and (self.start_date != "" or self.start_timestamp != ""):
			# both ends of date interval are specified
			if self.start_date != "":
				start = dateToTimestamp(self.start_date)
			else:
				start = self.start_timestamp

			if self.end_date != "":
				end = dateToTimestamp(self.end_date)
			else:
				end = self.end_timestamp

			req_interval = (start, end)

			covered = False
			for coverage in cache["coverage"]:
				coverage_interval = (coverage["start"], coverage["end"])
				# if date interval not covered => extract
				if intervalCovered(req_interval, coverage_interval):
					covered = True
					break

			# data interval is covered, retrieve a list of all relevant commits
			if covered:
				# retrieve repository info artefact
				data = {
					"artefact": ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO,
					"repository": self.repository
				}

				info_found, info_artefact = self.ff.bake("etcdstoragereader").call(data)
				if info_found:
					self.repository_info = info_artefact

					# retrieve commits (if any of them not found, continue)
					self.repository_commits = self._retrieveCommitsFromCache(cache, start, end)

					return True

		# ================================================================
		# cache not found, info not retrieved or data interval not covered
		# ================================================================

		# extract artefacts
		data = self._extractRepositoryData()
		# store commit artefacts, get a list of stored commits and into artefact
		extracted_info_artefact = data["info"]
		stored_commits, not_stored_commits = self._storeRepositoryData(data["commits"])

		# if some commits are not stored, break the coverate interval into subintervals
		extracted_item_set_cache = ItemSetCache().addItems(stored_commits, not_stored_commits)

		# return unchanged repository info artefact
		self.repository_info = extracted_info_artefact
		# update the artefact to be stored with a list of stored commits
		extracted_info_artefact["coverage"] = extracted_item_set_cache.intervals()
		# update the list of commits being stored
		extracted_info_artefact["commits"] = map(lambda l: l["item"], extracted_item_set_cache.items())
		# TODO(jchaloup): check for empty list of commits => we end here

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
		# info found
		else:
			extracted_item_set_cache.addItems(
				# reconstruct points info_artefact
				self._generatePointsFromRepositoryInfoArtefact(info_artefact)
			)

			# merge both infos
			updated_repository_info = self._mergeRepositoryInfoArtefacts(
				info_artefact,
				extracted_info_artefact,
				extracted_item_set_cache.intervals()
			)
		# store both new info and cache
		self._storeInfo(updated_repository_info)
		self._storeCache(
			self._generateNewCache(extracted_item_set_cache)
		)

		return True
