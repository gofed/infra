#
# Extraction of artefacts from an distribution package
#
# Inspired by scanupstreamrepository act
#

from infra.system.core.meta.metaact import MetaAct
from infra.system.resources.specifier import ResourceSpecifier
from infra.system.resources import types
from infra.system.helpers.utils import getScriptDir
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD,
	ARTEFACT_CACHE_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS
)

from gofed_lib.utils import dateToTimestamp
from infra.system.helpers.itemsetcache.itemsetcache import ItemSetCache
from gofed_lib.utils import intervalCovered
from infra.system.core.acts.types import ActDataError
import logging
import json

class ScanDistributionPackageAct(MetaAct):

	def __init__(self):
		MetaAct.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__)
		)

		self.itemset_info = {}
		self.items = {}

		self.product = ""
		self.distribution = ""
		self.package = ""
		self.start_timestamp = 0
		self.end_timestamp = 0

	def setData(self, data):
		"""Validation and data pre-processing"""
		if not self._validateInput(data):
			return False

		self.product = data["product"]
		self.distribution = data["distribution"]
		self.package = data["package"]

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

		return True

	def getData(self):
		"""Validation and data post-processing"""
		return {
			"package_builds": self.itemset_info,
			"builds": self.items
		}

	def _extractItemSetInfo(self):
		# no cache => extract the data
		data = {
			"product": self.product,
			"distribution": self.distribution,
			"package": self.package
		}

		if self.start_timestamp != "":
			data["start_timestamp"] = self.start_timestamp
		elif self.start_date != "":
			data["start_date"] = self.start_date

		if self.end_timestamp != "":
			data["end_timestamp"] = self.end_timestamp
		elif self.end_date != "":
			data["end_date"] = self.end_date

		return self.ff.bake("distributionpackagebuildsextractor").call(data)

	def _storeItems(self, items, item_key="name", point_key="build_ts"):
		"""Store all items, return list of stored commits

		:param items: artefact/item
		:type  items: [artefact]
		"""
		stored_items = []
		not_stored_items = []
		for item in items:
			# even if a commit does not get stored, index it
			self.items[item["name"]] = item

			if not self.store_artefacts:
				continue

			# store item
			try:
				self.ff.bake(self.write_storage_plugin).call(item)
			except IOError as e:
				not_stored_items.append({
					"item": item[item_key],
					"point": item[point_key]
				})
				logging.error("Unable to store item: %s. Cause: e" % (json.dumps(item), e))
				continue

			stored_items.append({
				"item": item[item_key],
				"point": item[point_key]
			})

		return (stored_items, not_stored_items)

	def _generateNewCache(self, itemsetcache):
		# construct cache
		return {
			"artefact": ARTEFACT_CACHE_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS,
			"product": self.product,
			"distribution": self.distribution,
			"package": self.package,
			"coverage": itemsetcache.intervals(),
			"builds": itemsetcache.items()
		}

	def _mergeItemSetInfoArtefacts(self, info1, info2, coverage):
		# merged info artefact
		return {
			"artefact": ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS,
			"product": info2["product"],
			"distribution": info2["distribution"],
			"package": info2["package"],
			"builds": list(set(info1["builds"]) | set(info2["builds"])),
			"coverage": coverage
		}

	def _storeCache(self, cache):
		if not self.store_artefacts:
			return

		try:
			self.ff.bake(self.write_storage_plugin).call(cache)
		except IOError as e:
			# I would like to have the cache saved too
			# Again, for just retrieval of data this is not necassary
			raise ActDataError("Unable to store cache: %s. Cause: %s" % (json.dumps(cache), e))

	def _storeInfo(self, info):
		if not self.store_artefacts:
			return

		try:
			self.ff.bake(self.write_storage_plugin).call(info)
		except IOError as e:
			# TODO(jchaloup): if the act is run just to retrieve the artefacts, log the error and continue
			# if it is meant for scanning, raise the exception
			raise ActDataError("Unable to store itemset info artefact: %s" % (json.dumps(info), e))

	def _generatePointsFromItemSetInfoArtefact(self, itemset_info, item_key="name", point_key="build_ts"):
		"""Generate list of (item, point) pairs from itemset info artefact.
		If any read from a storage fails, the cache can be incomplete.
		Let's use what we get and give the cache another chance to get reconstructed in another scan.

		:param itemset_info: itemset info artefact
		:type  itemset_info: artefact
		"""
		if not self.retrieve_artefacts:
			return []

		items = []
		for item in itemset_info["builds"]:
			# construct a storage request for each item
			data = {
				"artefact": ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD,
				"product": self.product,
				item_key: item
			}

			# retrieve item point for each item
			try:
				item_data = self.ff.bake(self.read_storage_plugin).call(data)
			except KeyError:
				continue

			items.append({
				"item": item_data[item_key],
				"point": item_data[point_key]
			})

		return items

	def _retrieveItemsFromCache(self, cache, info, start, end):
		if not self.retrieve_artefacts:
			return {}

		items = {}
		for item in filter(lambda l: l["point"] >= start and l["point"] <= end, cache["builds"]):
			# construct a storage request for each item
			data = {
				"artefact": ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD,
				"product": self.product,
				"name": item["item"]
			}

			# retrieve item point for each item
			try:
				item_data = self.ff.bake(self.read_storage_plugin).call(data)
			except KeyError:
				continue

			items[item["item"]] = item_data

		return items

	def execute(self):
		"""Impementation of concrete data processor"""

		self.itemset_info = {}
		self.items = {}

		# check storage
		# read the current list of builds stored in storage
		# if the youngest build is younger than end_date, no need to extract data
		# if so, filter out builds older than start_date
		# otherwise extract the missing builds from build system,
		# update the current list of builds and return the relevant sublist
		# with all builds inside the sublist

		# cached?
		data = {
			"artefact": ARTEFACT_CACHE_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS,
			"product": self.product,
			"distribution": self.distribution,
			"package": self.package
		}

		cache_found = False
		if self.retrieve_artefacts:
			cache_found = True
			try:
				cache = self.ff.bake(self.read_storage_plugin).call(data)
			except KeyError:
				cache_found = False

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
					"artefact": ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS,
					"product": self.product,
					"distribution": self.distribution,
					"package": self.package
				}

				info_found, itemset_info = self.ff.bake(self.read_storage_plugin).call(data)
				if info_found:
					# retrieve commits (if any of them not found, continue)
					self.items = self._retrieveItemsFromCache(cache, itemset_info, start, end)
					self.itemset_info = itemset_info

					return True

		# ================================================================
		# cache not found, info not retrieved or data interval not covered
		# ================================================================

		# extract artefacts
		data = self._extractItemSetInfo()
		# store item artefacts, get a list of stored items and item set info artefact
		extracted_itemset_info = data["package_builds"]
		stored_items, not_stored_items = self._storeItems(data["builds"])

		# create the cache from extracted item
		extracted_itemset_cache = ItemSetCache().addItems(stored_items, not_stored_items)

		# return unchanged repository that was extracted
		self.itemset_info = extracted_itemset_info
		# update the coverage intervals with the list of stored items
		extracted_itemset_info["coverage"] = extracted_itemset_cache.intervals()
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
			"artefact": ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS,
			"product": self.product,
			"distribution": self.distribution,
			"package": self.package
		}

		info_found = False
		if self.retrieve_artefacts:
			info_found = True
			try:
				itemset_info = self.ff.bake(self.read_storage_plugin).call(data)
			except KeyError:
				info_found = False

		# info not found
		if not info_found:
			updated_itemset_info = extracted_itemset_info
		# info found
		else:
			extracted_itemset_cache.addItems(
				# reconstruct points
				self._generatePointsFromItemSetInfoArtefact(itemset_info)
			)

			# merge both infos
			updated_itemset_info = self._mergeItemSetInfoArtefacts(
				itemset_info,
				extracted_itemset_info,
				extracted_itemset_cache.intervals()
			)

		# store both new info and cache
		self._storeInfo(updated_itemset_info)
		self._storeCache(
			self._generateNewCache(extracted_itemset_cache)
		)

		return True
