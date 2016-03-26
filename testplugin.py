from system.plugins.repositorydataextractor.extractor import RepositoryDataExtractor
from system.plugins.repositorydataextractor.fake_extractor import FakeRepositoryDataExtractor
import json

if __name__ == "__main__":

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
