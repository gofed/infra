from gofed_lib.utils import intervalsOverlap

class CacheIntervalMerger(object):

	def __init__(self):
		pass

	def _overlap(self, interval1, interval2):
		s1 = interval1["start_timestamp"]
		e1 = interval1["end_timestamp"]
		s2 = interval2["start_timestamp"]
		e2 = interval2["end_timestamp"]

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
			"start_timestamp": min(interval1["start_timestamp"], interval2["start_timestamp"]),
			"end_timestamp": max(interval1["end_timestamp"], interval2["end_timestamp"])
		}

	def merge(self, intervals1, intervals2):
		"""Merge two caches

		:param cache: the current cache
		:type  cache: dict
		:param newcache: cache to be merged with the current cash
		:type  newcache: dict
		"""

		# merge coverages.
		# Asumption: none of the intervals overlap
		#
		# Each interval in newcache can overlap with one or more intervals
		# in cache. If so, take all such intervals and merge them with the
		# newcache's intervals.
		#
		# Algorithm:
		# 1. for each interval in newcache:
		# 	o_intervals = findOverlappingIntervalsInCache(cache, interval)
		#	n_interval = merge(o_intervals + interval)
		# 2. merge all overlapping n_intervals
		n_intervals = []
		# TODO(jchaloup): this can be done in linear time!!!
		for interval1 in intervals1:
			for interval2 in intervals2:
				if self._overlap(interval1, interval2):
					n_intervals.append(self._mergeIntervals(interval1, interval2))

		# For testing purposes
		#n_intervals = [
		#	{"start_timestamp": 1, "end_timestamp": 2},
		#	{"start_timestamp": 3, "end_timestamp": 6},
		#	{"start_timestamp": 5, "end_timestamp": 8},
		#	{"start_timestamp": 10, "end_timestamp": 12},
		#	{"start_timestamp": 13, "end_timestamp": 15},
		#	{"start_timestamp": 16, "end_timestamp": 18},
		#	{"start_timestamp": 11, "end_timestamp": 17}
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
