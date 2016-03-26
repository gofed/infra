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
from infra.system.helpers.cacheintervalmerger import CacheIntervalMerger
from gofed_lib.utils import intervalCovered

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
	def _extractData(self):
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

		data = self.ff.bake("repositorydataextractor").call(data)
		# TODO(jchaloup): just for testing purposes, make it configurable
		# store artefacts into storage
		for artefact in data:
			rdata = self.ff.bake("etcdstoragewriter").call(artefact)

		# construct cache
		cache_list = []
		start_timestamp = 0
		end_timestamp = 0
		for artefact in data:
			if artefact["artefact"] == ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT:
				cache_list.append({
					"c": artefact["commit"],
					"d": artefact["cdate"]
				})
			elif artefact["artefact"] == ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO:
				start_timestamp = artefact["start_timestamp"]
				end_timestamp = artefact["end_timestamp"]

		# TODO(jchaloup): just for testing purposes, make it configurable
		# store the cache
		return {
			"artefact": ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS,
			"repository": self.repository,
			"coverage": [{
				"start_timestamp": start_timestamp,
				"end_timestamp": end_timestamp
			}],
			"commits": cache_list
		}

	def _mergeCommits(self, commits1, commits2):
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
		cache["commits"] = self._mergeCommits(cache1["commits"], cache2["commits"])

		return cache

	def _storeCache(self, cache):
		if not self.ff.bake("etcdstoragewriter").call(cache):
			# TODO(jchaloup): this needs to be handled if configured to run
			logging.error("Unable to store cache")


	def execute(self):
		"""Impementation of concrete data processor"""

		# check storage
		# I can not check for spec file specific macros as I need project
		# to get artefact from a storage. Without the project I can not
		# get artefact from a storage.

		self.repository_info = {}
		self.repository_commits = []

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

		ok, cache = self.ff.bake("etcdstoragereader").call(data)
		if ok:
			# is (start_date, end_date) in coverage?
			# if end_date not defined => extract
			# if start_date not defined => extract
			if self.end_date == "" or self.start_date == "":
				# extract data and retrieve their cache
				newcache = self._extractData()

				# extend the current cache
				cache = self._mergeCaches(
					cache,
					newcache
				)

				# save the cache
				self._storeCache(cache)
				return True

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

			print covered
			if not covered:
				# extract data and retrieve their cache
				newcache = self._extractData()

				# extend the current cache
				cache = self._mergeCaches(
					cache,
					newcache
				)

				# save the cache
				self._storeCache(cache)

			return True

		# create fresh new cache
		cache = self._extractData()
		self._storeCache(cache)

		return True
