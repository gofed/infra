from infra.system.core.factory.functionfactory import FunctionFactory
from infra.system.resources.specifier import ResourceSpecifier
from infra.system.resources import types

import logging
import json

logging.basicConfig(level=logging.INFO)

def getAPI():

	data = {
		"resource": "/home/jchaloup/Packages/golang-github-bradfitz-http2/fedora/golang-github-bradfitz-http2/http2-f8202bc903bda493ebba4aa54922d78430c2c42f",
		"directories_to_skip": ["Godeps","hack"],
		"project": "github.com/bradfitz/http2",
		"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
		"ipprefix": "github.com/bradfitz/http2"
	}

	data["resource"] = ResourceSpecifier().generateUserDirectory(data["resource"], type = types.RESOURCE_TYPE_DIRECTORY)

	ff = FunctionFactory()
	return ff.bake("gosymbolsextractor").call(data)

def getAPI1():

	data = {
		"resource": "/home/jchaloup/Packages/etcd/rhel/etcd/etcd-2.2.2",
		"directories_to_skip": ["Godeps","hack"],
		"project": "github.com/coreos/etcd",
		"commit": "b4bddf685b26b4aa70e939445044bdeac822d042",
		"ipprefix": "github.com/coreos/etcd"
	}

	data["resource"] = ResourceSpecifier().generateUserDirectory(data["resource"], type = types.RESOURCE_TYPE_DIRECTORY)

	ff = FunctionFactory()
	return ff.bake("gosymbolsextractor").call(data)

def getAPI2():

	data = {
		"resource": "/home/jchaloup/Packages/etcd/fedora/etcd/etcd-2.2.5",
		#"resource": "/home/jchaloup/Packages/kubernetes/fedora/kubernetes/origin-cffae0523cfa80ddf917aba69f08508b91f603d5",
		"directories_to_skip": ["Godeps","hack"],
		"project": "github.com/coreos/etcd",
		"commit": "bdee27b19e8601ffd7bd4f0481abe9bbae04bd09",
		"ipprefix": "github.com/coreos/etcd"
	}

	data["resource"] = ResourceSpecifier().generateUserDirectory(data["resource"], type = types.RESOURCE_TYPE_DIRECTORY)

	ff = FunctionFactory()
	return ff.bake("gosymbolsextractor").call(data)

def storeExportedAPI():
	exported_api1 = getAPI1()
	exported_api2 = getAPI2()

	# store the data
	ff = FunctionFactory()
	ff.bake("etcdstoragewriter").call(exported_api1[1])
	ff.bake("etcdstoragewriter").call(exported_api2[1])

	ff.bake("etcdstoragewriter").call(exported_api1[0])
	ff.bake("etcdstoragewriter").call(exported_api2[0])

def retrieveExportedAPI():
	data = {
		"artefact": "golang-project-exported-api",
		"project": "github.com/coreos/etcd",
		"commit": "b4bddf685b26b4aa70e939445044bdeac822d042"
	}

	ff = FunctionFactory()
	_, exported_api1 = ff.bake("etcdstoragereader").call(data)

	data = {
		"artefact": "golang-project-exported-api",
		"project": "github.com/coreos/etcd",
		"commit": "bdee27b19e8601ffd7bd4f0481abe9bbae04bd09"
	}

	_, exported_api2 = ff.bake("etcdstoragereader").call(data)

	return (exported_api1, exported_api2)

getAPI2()
exit(1)

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

#print json.dumps(exported_api2)
#exit(1)

ff = FunctionFactory()
data = ff.bake("goapidiff").call(data)
ff.bake("etcdstoragewriter").call(data)

print(json.dumps(data))
