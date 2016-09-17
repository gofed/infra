#  Go project content metadata extractor

Extract meta information about a go project:

* list of licenses
* list of docs
* list of directories with bundled/vendored dependencies
* list of directories with no go source code file

Bundled/vendored dependencies directory detection is based on recognition of know prefixes and directory hiearchies:

* Godeps: expected ``Godeps/_workspace/src`` path
* vendored: expected ``vendor/src`` path
* external: expected ``external`` path

At the same time every detected dependency directory must contains at least on of the following directories:

* github.com
* google.golang.org
* bitbucket.org
* golang.org
* gopkg.in
* speter.net
* k8s.io

## Input schema

* [input_schema.json](https://github.com/gofed/infra/blob/master/system/plugins/goprojectcontentmetadataextractor/input_schema.json)

E.g.

```
{
	"project": "github.com/golang/net",
	"commit": "e45385e9b226f570b1f086bf287b25d3d4117776",
	"resource": "/home/user/goproject"
}
```

## Provided artefacts

* [ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-project-content-metadata.json)

## Usage

```python
from infra.system.core.factory.functionfactory import FunctionFactory

function = FunctionFactory().bake("goprojectcontentmetadataextractor")
data = {
	"project": "github.com/golang/net",
	"commit": "e45385e9b226f570b1f086bf287b25d3d4117776",
	"resource": "/home/user/goproject"
}

artefacts = function.call(data)
```
