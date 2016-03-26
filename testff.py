from infra.system.core.functions.functionfactory import FunctionFactory
import json

ff = FunctionFactory()
f = ff.bake("gosymbolsextractor")

data = {
	"resource": "/home/jchaloup/Packages/golang-github-bradfitz-http2/fedora/golang-github-bradfitz-http2/http2-f8202bc903bda493ebba4aa54922d78430c2c42f",
	"directories_to_skip": ["Godeps","hack"],
	"project": "github.com/bradfitz/http2",
	"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
	"ipprefix": "github.com/bradfitz/http2"
}


print json.dumps(f.call(data))
