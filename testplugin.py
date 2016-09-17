#from gofedinfra.system.plugins.repositorydataextractor.extractor import RepositoryDataExtractor
#from gofedinfra.system.plugins.repositorydataextractor.fake_extractor import FakeRepositoryDataExtractor
import json

from gofedinfra.system.plugins.distributionpackagebuildsextractor.extractor import DistributionPackageBuildsExtractor

def runRepositoryDataExtractor():
	extractor = RepositoryDataExtractor()
	extractor.setData({
		"repository": {
			"provider": "github",
			"username": "coreos",
			"project": "etcd"
		},
		"resource": "/home/jchaloup/Packages/etcd/upstream/etcd"
		#"start_date": "2016-03-22" #,
		#"end_date": "2016-03-26"
	})

	extractor.execute()
	extractor.getData()
	#print json.dumps(act.getData())

def runDistributionPackageBuildsExtractor():
	extractor = DistributionPackageBuildsExtractor()
	print extractor.setData({
		#"package": "golang-bitbucket-ww-goautoneg",
		"package": "etcd",
		"product": "Fedora",
		"distribution": "f24",
		"start_timestamp": 1400131190,
		"end_timestamp": 1460131190
	})

	print extractor.execute()
	print json.dumps(extractor.getData())

if __name__ == "__main__":

	#runRepositoryDataExtractor()
	runDistributionPackageBuildsExtractor()

