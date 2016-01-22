from system.plugins.metaprocessor import MetaProcessor
from SpecParser import SpecParser

class SpecDataExtractor(MetaProcessor):

	def __init__(self):
		# received data
		self.specfile = ""
		self.distribution = ""
		self.product = ""
		self.package = ""

		# extracted data
		self.commit = ""
		self.project = ""
		self.ipprefix = ""

	def setData(self, data):
		"""Validation and data pre-processing"""
		# TODO(jchaloup): validate data with JSON Schema

		self.specfile = data["specfile"]

	def getData(self):
		"""Validation and data post-processing"""
		data = []

		data.append(self._generateGolangProjectInfoFedora())
		data.append(self._generateGolangProjectToPackageName())
		data.append(self._generateGolangIPPrefixToPackageName())

		return data

	def _generateGolangProjectInfoFedora(self):
		# TOOD(jchaloup): generate json from class attributes
		print "commit: %s" % self.commit

		raise NotImplementedError

	def _generateGolangProjectToPackageName(self):
		# TOOD(jchaloup): generate json from class attributes
		print "project: %s" % self.project

		raise NotImplementedError

	def _generateGolangIPPrefixToPackageName(self):
		# TOOD(jchaloup): generate json from class attributes
		print "ipprefix: %s" % self.ipprefix

		raise NotImplementedError

	def execute(self):
		"""Impementation of concrete data processor"""
		sp = SpecParser(self.specfile)
		if not sp.parse():
			return False

		# RFE(jchaloup): if %commit is not found => log this to special channel
		self.commit = sp.getMacro("commit")
		if self.commit == "":
			logging.error("commit not found")
			return False

		# RFE(jchaloup): if %import_path is not found => log this to special channel
		self.project = sp.getMacro("provider_prefix")
		if self.project == "":
			self.project = sp.getMacro("import_path")
		if self.project == "":
			logging.error("project not found")
			return False

		# RFE(jchaloup): if %import_path is not found => log this to special channel
		self.ipprefix = sp.getMacro("import_path")
		if self.ipprefix == "":
			logging.error("import path prefix not found")
			return False

		return True

