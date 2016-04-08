from infra.system.plugins.distributionbuildextractor.extractor import DistributionBuildExtractor


class FakeDistributionBuildExtractor(DistributionBuildExtractor):

	def __init__(self):
		DistributionBuildExtractor.__init__(self)

	def setData(self, data):
		data = {
			"project": "example",
			"product": "example",
			"distribution": "example",
			"repository": "example",
			"clone_url": "example"
		}
		DistributionBuildExtractor.setData(self,data)

	def getData(self):
		return DistributionBuildExtractor.getData(self)

	def execute(self):
		build = {"bdate": "2015-05-21",
				 "author": "jchaloup",
				 "rpms": ["etcd-devel-2.0.11-1.fc21.i686.rpm"],
				 "name": "etcd-2.0.11-1.fc21",
				 "id": 638275,
				 "architectures": ["armv7hl", "src", "i686", "x86_64"]}
		self.builds.append(build)

		return True
