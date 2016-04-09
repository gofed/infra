#
# Provide a cache for pairs (item, number).
# The cache accepts intervals of pairs and provides:
# - test of coverage if a given pair (item, number) is contained in at least one interval
# - test of coverage if a given interval is pairs is subset of at least one interval
# - provides a list of all non-overlaping intervals
# - when two intervals overlaps, they are merged together
#
# Primary use for:
# - repository info: consists of list of commits, each commit has its commit data.
#   The problem is to get a given interval of commits from cache or report the interval is not covered
# - package builds info: consists of lists of builds, each build has its build time.
#   The problem is to get a given interval of builds from cache or report the interval is not covered

from gofed_lib.utils import intervalsOverlap

class ItemSetCache(object):

	def __init__(self):
		# keep the list in sorted order
		self._intervals = []
		self._items = []

	def addIntervals(self, intervals):
		"""Add intervals into the cache.

		:param intervals: list of intervals
		:type  intervals: [interval]
		"""
		pass

	def addItems(self, items, breakpoints = []):
		"""Add list of items into the cache.
		If breakpoints list is non-empty, decompose the items into interval.
		Otherwise construct a single interval

		:param items: list of items
		:type  items: [dict]
		:param breakpoints: list of points to break interval at
		:type  breakpoints: [string]
		"""
		intervals = CoverageIntervalBreaker().decompose(items, breakpoints)
		self._items = self._items + items
		self._intervals = CoverageIntervalMerger().merge(self._intervals, intervals)

		return self

	def intervals(self):
		return self._intervals

	def items(self):
		return self._items

	def cache(self):
		return {
			"coverage": self._intervals,
			"items": self._items
		}

class CoverageIntervalBreaker(object):

	def decompose(self, interval, breakpoints):
		items = interval + breakpoints
		items = sorted(items, key = lambda item: item["point"])
		items = map(lambda l: {"item": "", "point": l["point"]} if l in breakpoints else l, items)

		# decompose
		items_len = len(items)
		index = 0
		coverage = []

		while index < items_len:
			# find start of a segment
			while index < items_len and items[index]["item"] == "":
				index = index + 1

			# end of the list?
			if index >= items_len:
				break

			start = items[index]["point"]
			# find end of the segment
			end = items[index]["point"]
			while index < items_len and items[index]["item"] != "":
				end = items[index]["point"]
				index = index + 1

			# end of segment or entire list found
			coverage.append({
				"start": start,
				"end": end
			})

		return coverage

class CoverageIntervalMerger(object):

	def _overlap(self, interval1, interval2):
		s1 = interval1["start"]
		e1 = interval1["end"]
		s2 = interval2["start"]
		e2 = interval2["end"]

		return intervalsOverlap((s1, e1), (s2, e2))

	def _mergeIntervals(self, interval1, interval2):
		"""Merge two intervals

		:param interval1: interval
		:type  interval1: dict
		:param interval2: interval
		:type  interval2: dict
		"""

		# If two intervals overlap, just take minimum of s's and maximum of e's
		return {
			"start": min(interval1["start"], interval2["start"]),
			"end": max(interval1["end"], interval2["end"])
		}

	def merge(self, intervals1, intervals2):
		"""Merge two caches

		:param intervals1: list of date intervals
		:type  intervals1: [{}]
		:param intervals2: list of date intervals
		:type  intervals2: [{}]
		"""
		n_intervals = sorted(intervals1 + intervals2, key = lambda interval: interval["start"])

		# For testing purposes
		#n_intervals = [
		#	{"start": 1, "end": 2},
		#	{"start": 3, "end": 6},
		#	{"start": 5, "end": 8},
		#	{"start": 10, "end": 12},
		#	{"start": 13, "end": 15},
		#	{"start": 16, "end": 18},
		#	{"start": 11, "end": 17}
		#]

		# overlapping
		overlap = True
		while overlap:
			overlap = False
			interval_count = len(n_intervals)
			for i in range(0, interval_count - 1):
				if n_intervals[i] == {}:
					continue

				if self._overlap(n_intervals[i], n_intervals[i + 1]):
					overlap = True
					n_intervals[i + 1] = self._mergeIntervals(n_intervals[i], n_intervals[i + 1])
					n_intervals[i] = {}

			# filter out all empty intervals
			n_intervals = filter(lambda l: l != {}, n_intervals)

			if not overlap:
				break

			interval_count = len(n_intervals)
			for i in reversed(range(1, interval_count)):
				if n_intervals[i] == {}:
					continue

				if self._overlap(n_intervals[i], n_intervals[i - 1]):
					overlap = True
					n_intervals[i - 1] = self._mergeIntervals(n_intervals[i], n_intervals[i - 1])
					n_intervals[i] = {}

			# filter out all empty intervals
			n_intervals = filter(lambda l: l != {}, n_intervals)

		return n_intervals

if __name__ == "__main__":
	intervals1 = [
		{"item": "a", "point": 1},
		{"item": "b", "point": 2},
		{"item": "c", "point": 4},
		{"item": "d", "point": 14},
		{"item": "e", "point": 15},
		{"item": "f", "point": 18},
	]

	breakpoints1 = [
		{"item": "aa", "point": 3},
		{"item": "ab", "point": 6},
	]

	cache = ItemSetCache().addItems(intervals1, breakpoints1)

	print cache.intervals()
	print cache.items()

	intervals2 = [
		{"item": "g", "point": 17},
		{"item": "h", "point": 19},
		{"item": "i", "point": 21},
		{"item": "j", "point": 23},
	]

	breakpoints2 = [
		{"item": "ba", "point": 20},
		{"item": "bb", "point": 22},
	]

	cache.addItems(intervals2, breakpoints2)

	print cache.intervals()
	print cache.items()

	print ""
	print cache.cache()
