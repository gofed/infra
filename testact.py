from system.core.factory.actfactory import ActFactory
import json

def prepareSpecModelDataProviderActWithUpstream():
	data = {
		"type": "upstream_source_code",
		"project": "github.com/bradfitz/http2",
		"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
		"directories_to_skip": ["Godeps","hack"],
		"ipprefix": "github.com/bradfitz/http2"
	}

	act = ActFactory().bake("spec-model-data-provider")

	return (data, act)

def prepareSpecModelDataProviderActWithUserDirectory():

	data = {
		"type": "user_directory",
		#"resource": "/home/jchaloup/Packages/golang-github-bradfitz-http2/fedora/golang-github-bradfitz-http2/http2-f8202bc903bda493ebba4aa54922d78430c2c42f",
		"resource": "/home/jchaloup/Packages/etcd/rhel/etcd/etcd-2.2.2",
		"directories_to_skip": ["Godeps","hack"],
		"ipprefix": "github.com/bradfitz/http2"
	}

	act = ActFactory().bake("spec-model-data-provider")

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

	act = ActFactory().bake("scan-distribution-build")

	return (data, act)

def prepareGoCodeInspectionActWithUpstream():
	data = {
		"type": "upstream_source_code",
		"project": "github.com/bradfitz/http2",
		"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
		"directories_to_skip": ["Godeps","hack"],
		"ipprefix": "github.com/bradfitz/http1"
	}

	act = ActFactory().bake("go-code-inspection")

	return (data, act)

def prepareScanUpstreamRepositoryAct():
	data = {
		"repository": {
			"provider": "github",
			"username": "coreos",
			"project": "etcd"
		},
		"commit": "5e6eb7e19d6385adfabb1f1caea03e732f9348ad",
		#"start_date": "2016-03-23",
		#"end_date": "2016-03-25"
		#"start_date": "2016-03-10",
		#"end_date": "2016-03-22"
		"start_date": "2016-03-15",
		"end_date": "2016-03-17"

	}

	act = ActFactory().bake("scan-upstream-repository")

	return (data, act)

def prepareGoApiDiff():
	data = {
		"reference": {
			"type": "upstream_source_code",
			"project": "github.com/bradfitz/http2",
			"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
			"ipprefix": "github.com/bradfitz/http1"
		},
		"compared_with": {
			"type": "upstream_source_code",
			"project": "github.com/bradfitz/http2",
			"commit": "953b51136f12cb27503bec0f659432fd1fa97770",
			"ipprefix": "github.com/bradfitz/http1"
		}
	}

	act = ActFactory().bake("go-exported-api-diff")

	return (data, act)


if __name__ == "__main__":

	#data, act = prepareSpecModelDataProviderActWithUpstream()
	#data, act = prepareSpecModelDataProviderActWithUserDirectory()
	#data, act = prepareScanDistributionBuildAct()
	#data, act = prepareGoCodeInspectionActWithUpstream()
	#data, act = prepareScanUpstreamRepositoryAct()
	data, act = prepareGoApiDiff()

	print json.dumps(act.call(data))

