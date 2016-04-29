from infra.system.plugins.distributionpackagebuildsextractor.extractor import DistributionPackageBuildsExtractor
from gofed_lib.distribution.clients.koji.fakeclient import FakeKojiClient

class FakeDistributionPackageBuildsExtractor(DistributionPackageBuildsExtractor):

	def __init__(self):
		DistributionPackageBuildsExtractor.__init__(self)
		self._client = FakeKojiClient()

	def setData(self, data):
		return DistributionPackageBuildsExtractor.setData(self, data)

	def getData(self):
		return DistributionPackageBuildsExtractor.getData(self)

	def execute(self):
		return DistributionPackageBuildsExtractor.execute(self)
