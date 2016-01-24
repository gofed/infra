from system.plugins.gosymbolextractor.extractor import GoSymbolExtractor
from system.plugins.goapidiff.analyzer import GoApiDiff
import json

data = {
	"source_code_directory": "/home/jchaloup/Packages/etcd/rhel/etcd/etcd-2.2.2",
	"directories_to_skip": ["Godeps","hack"],
	"project": "github.com/coreos/etcd",
	"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
	"ipprefix": "github.com/coreos/etcd"
}

p = GoSymbolExtractor()
p.setData(data)
p.execute()
exported_api1 = p.getData()

data = {
	"source_code_directory": "/home/jchaloup/Packages/etcd/fedora/etcd/etcd-2.2.4",
	"directories_to_skip": ["Godeps","hack"],
	"project": "github.com/coreos/etcd",
	"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
	"ipprefix": "github.com/coreos/etcd"
}

p = GoSymbolExtractor()
p.setData(data)
p.execute()
exported_api2 = p.getData()


data = {
	"exported_api_1": exported_api1[1],
	"exported_api_2": exported_api2[1]
}

p = GoApiDiff()
p.setData(data)
p.execute()
