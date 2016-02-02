from system.plugins.gosymbolextractor.extractor import GoSymbolExtractor
from system.plugins.goapidiff.analyzer import GoApiDiff
import json

from system.artefacts import artefacts
from system.plugins.storages.simpleetcdstorage.storagewritter import StorageWritter

from system.plugins.storages.simpleetcdstorage.storagereader import StorageReader

import logging
logging.basicConfig(level=logging.INFO)

def getAPI():

	data = {
		"source_code_directory": "/home/jchaloup/Packages/golang-github-bradfitz-http2/fedora/golang-github-bradfitz-http2/http2-f8202bc903bda493ebba4aa54922d78430c2c42f",
		"directories_to_skip": ["Godeps","hack"],
		"project": "github.com/bradfitz/http2",
		"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
		"ipprefix": "github.com/bradfitz/http2"
	}

	p = GoSymbolExtractor()
	p.setData(data)
	p.execute()
	return p.getData()

def getAPI1():

	data = {
		"source_code_directory": "/home/jchaloup/Packages/etcd/rhel/etcd/etcd-2.2.2",
		"directories_to_skip": ["Godeps","hack"],
		"project": "github.com/coreos/etcd",
		"commit": "b4bddf685b26b4aa70e939445044bdeac822d042",
		"ipprefix": "github.com/coreos/etcd"
	}

	p = GoSymbolExtractor()
	p.setData(data)
	p.execute()
	return p.getData()

def getAPI2():

	data = {
		"source_code_directory": "/home/jchaloup/Packages/etcd/fedora/etcd/etcd-2.2.4",
		"directories_to_skip": ["Godeps","hack"],
		"project": "github.com/coreos/etcd",
		"commit": "bdee27b19e8601ffd7bd4f0481abe9bbae04bd09",
		"ipprefix": "github.com/coreos/etcd"
	}

	p = GoSymbolExtractor()
	p.setData(data)
	p.execute()
	return p.getData()

def storeExportedAPI():
	exported_api1 = getAPI1()
	exported_api2 = getAPI2()

	# store the data
	StorageWritter().store(exported_api1[1])
	StorageWritter().store(exported_api2[1])

def retrieveExportedAPI():
	data = {
		"artefact": "golang-project-exported-api",
		"project": "github.com/coreos/etcd",
		"commit": "b4bddf685b26b4aa70e939445044bdeac822d042"
	}

	_, exported_api1 = StorageReader().retrieve(data)

	data = {
		"artefact": "golang-project-exported-api",
		"project": "github.com/coreos/etcd",
		"commit": "bdee27b19e8601ffd7bd4f0481abe9bbae04bd09"
	}

	_, exported_api2 = StorageReader().retrieve(data)

	return (exported_api1, exported_api2)

#data = getAPI()
#driver = GolangProjectExportedAPIDriver()
#driver.store(data[1])
#exit(1)

#storeExportedAPI()

exported_api1, exported_api2 = retrieveExportedAPI()
data = {
	"exported_api_1": exported_api1,
	"exported_api_2": exported_api2
}

p = GoApiDiff()
p.setData(data)
p.execute()
data = p.getData()

StorageWritter().store(data)

print json.dumps(data)
