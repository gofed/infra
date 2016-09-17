# Periodically check content of resource_client and resource_provider
# and delete all files/directories that are older than a given amount of time
#
# resource_client and resource_provider have its own GC instance
import os
import time
import shutil
import logging
logging.basicConfig(level=logging.INFO)

class GarbageCollector(object):

	def __init__(self, working_directory, ttl = 300, verbose=False):
		"""Run garbage collector on downloaded and stored files

		:param working_directory: working directory
		:type  working_directory: string
		:param ttl: time to live for a file in seconds, 5 minutes should be enough for each plugin
		:type  ttl: int
		"""
		self.working_directory = working_directory
		if ttl < 0:
			ttl = 0

		self.ttl = ttl
		self._verbose = verbose

	def _deleteTree(self, root_directory):
		if self._verbose:
			logging.info("Removing %s" % root_directory)

		if os.path.isfile(root_directory):
			os.unlink(root_directory)
			return

		if os.path.isfile(root_directory):
			os.unlink(root_directory)
			return

		def _handleOsWalk(err):
			raise OSError(err)

		# first unlink all symlinks
		for dirName, subdirList, fileList in os.walk(root_directory, onerror = _handleOsWalk):
			for file in fileList:
				full_path = os.path.join(dirName, file)
				if os.path.islink(full_path):
					os.unlink(full_path)

		# remove entire directory tree
		shutil.rmtree(root_directory)

	def oneRound(self):
		"""Run only one round of GC
		"""
		self._runCollector()

	def _runCollector(self):


		max_ttl_timestamp = int(time.time()) - self.ttl

		if self._verbose:
			logging.info("====Running GC====")

		direct_dirs = []
		direct_files = []

		def _handleOsWalk(err):
			raise OSError(err)

		for dirName, subdirList, fileList in os.walk(self.working_directory, onerror = _handleOsWalk):
			direct_dirs = subdirList
			direct_files = fileList
			break

		for file in direct_files:
			full_path = os.path.join(self.working_directory, file)
			# delete all files whose last modification time is less then ttl
			if os.path.getmtime(full_path) < max_ttl_timestamp:
				self._deleteTree(full_path)

		for dir in direct_dirs:
			full_path = os.path.join(self.working_directory, dir)
			# delete all files whose last modification time is less then ttl
			if os.path.getmtime(full_path) < max_ttl_timestamp:
				self._deleteTree(full_path)


	def run(self):
		while True:
			self._runCollector()
			time.sleep(self.ttl)

