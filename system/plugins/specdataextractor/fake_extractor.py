from system.plugins.specdataextractor.extractor import SpecDataExtractor


class FakeSpecDataExtractor(SpecDataExtractor):

	def __init__(self):
		SpecDataExtractor.__init__(self)

	def setData(self, data):
		data = {"product": "Fedora", "distribution": "f22", "package": "etcd", "specfile": "fullpathtospecfile" }

		SpecDataExtractor.setData(self,data)

	def getData(self):
		"""Validation and data post-processing"""

		return SpecDataExtractor.getData(self)

	def execute(self):
		self.project = "github.com/coreos/etcd"
		self.commit = "729b530c489a73532843e664ae9c6db5c686d314"
		self.lastupdated = "2015-12-12"
		self.ipprefix = "github.com/coreos/etcd"
