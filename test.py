from system.plugins.gosymbolextractor.extractor import GoSymbolExtractor
import json

data = {
	"source_code_directory": "/home/jchaloup/Packages/golang-github-bradfitz-http2/fedora/golang-github-bradfitz-http2/http2-f8202bc903bda493ebba4aa54922d78430c2c42f",
	"directories_to_skip": ["Godeps","hack"],
	"project": "github.com/bradfitz/http2",
	"commit": "f8202bc903bda493ebba4aa54922d78430c2c42f",
	"ipprefix": "github.com/bradfitz/http2"
}

config = "/home/jchaloup/Projects/gofed/infra/configs/GoSymbolExtractor.conf"

p = GoSymbolExtractor()
p.setData(data)
p.execute()
print json.dumps(p.getData())
