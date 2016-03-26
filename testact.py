from system.acts.specmodeldataprovider.act import SpecModelDataProviderAct
from system.acts.scandistributionbuild.act import ScanDistributionBuildAct
from system.acts.gocodeinspection.act import GoCodeInspectionAct
from system.acts.scanupstreamrepository.act import ScanUpstreamRepositoryAct
import json

def prepareSpecModelDataProviderActWithUpstream():
	data = {
		"type": "upstream_source_code",
		"project": "github.com/bradfitz/http2",
		"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
		"directories_to_skip": ["Godeps","hack"],
		"ipprefix": "github.com/bradfitz/http2"
	}

	act = SpecModelDataProviderAct()

	return (data, act)

def prepareSpecModelDataProviderActWithUserDirectory():

	data = {
		"type": "user_directory",
		#"resource": "/home/jchaloup/Packages/golang-github-bradfitz-http2/fedora/golang-github-bradfitz-http2/http2-f8202bc903bda493ebba4aa54922d78430c2c42f",
		"resource": "/home/jchaloup/Packages/etcd/rhel/etcd/etcd-2.2.2",
		"directories_to_skip": ["Godeps","hack"],
		"ipprefix": "github.com/bradfitz/http2"
	}

	act = SpecModelDataProviderAct()

	return (data, act)

def prepareScanDistributionBuildAct():

	data = {
		"product": "Fedora",
		"distribution": "f24",
		"build": {
			"name": "etcd-2.2.4-2.fc24",
			"rpms": [
				{
					"name": "etcd-devel-2.2.4-2.fc24.noarch.rpm",
					"skipped_directories": ["Godeps"]
				}
			]
		}
	}

	act = ScanDistributionBuildAct()

	return (data, act)

def prepareGoCodeInspectionActWithUpstream():
	data = {
		"type": "upstream_source_code",
		"project": "github.com/bradfitz/http2",
		"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
		"directories_to_skip": ["Godeps","hack"],
		"ipprefix": "github.com/bradfitz/http1"
	}

	act = GoCodeInspectionAct()

	return (data, act)

def prepareScanUpstreamRepositoryAct():
	data = {
		"repository": {
			"provider": "github",
			"username": "coreos",
			"project": "etcd"
		},
		"start_date": "2016-03-22",
		"end_date": "2016-03-25"
	}

	act = ScanUpstreamRepositoryAct()

	return (data, act)

if __name__ == "__main__":

	#data, act = prepareSpecModelDataProviderActWithUpstream()
	#data, act = prepareSpecModelDataProviderActWithUserDirectory()
	#data, act = prepareScanDistributionBuildAct()
	#data, act = prepareGoCodeInspectionActWithUpstream()
	data, act = prepareScanUpstreamRepositoryAct()

	print act.setData(data)

	print "Executing:"
	print act.execute()

	print "Getting:"
	print json.dumps(act.getData())
