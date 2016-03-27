from gofed_lib.utils import intervalsOverlap

class CacheIntervalBreaker(object):

	def __init__(self):
		pass

	def decompose(self, stored_commits, not_stored_commits):
		commits = stored_commits + not_stored_commits
		commits = sorted(commits, key = lambda commit: commit["d"])
		commits = map(lambda l: {"c": "", "d": l["d"]} if l in not_stored_commits else l, commits)

		# decompose
		commits_len = len(commits)
		index = 0
		coverage = []

		while index < commits_len:
			# find start of a segment
			while index < commits_len and commits[index]["c"] == "":
				index = index + 1

			# end of the list?
			if index >= commits_len:
				break

			start_date = commits[index]["d"]
			# find end of the segment
			end_date = commits[index]["d"]
			while index < commits_len and commits[index]["c"] != "":
				end_date = commits[index]["d"]
				index = index + 1

			# end of segment or entire list found
			coverage.append({
				"start_timestamp": start_date,
				"end_timestamp": end_date
			})

		return coverage

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

		:param intervals1: list of date intervals
		:type  intervals1: [{}]
		:param intervals2: list of date intervals
		:type  intervals2: [{}]
		"""
		n_intervals = sorted(intervals1 + intervals2, key = lambda interval: interval["start_timestamp"])

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
