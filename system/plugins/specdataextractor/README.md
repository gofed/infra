# Spec data extractor

Extract the following data from a spec file:

* commit (commit of a golang project specified in the spec file)
* provider prefix (repository provider where the project is avaiable)
* import path (import path prefix of the project that other projects can import)
* last change date (last time the spec file was modified)

Commit, provider prefix, resp. import path are extracted from
``%commit``, ``%provider_prefix``, resp. ``%import_path`` macros.

## Input schema

* [input_schema.json](https://github.com/gofed/infra/blob/master/system/plugins/specdataextractor/input_schema.json)

E.g.

```
{
	"product": "Fedora",
	"distribution": "rawhide",
	"package": "golang-github-coreos-pkg",
	"resource": "/home/user/goproject"
}
```

## Provided artefacts

* [ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-project-to-package-name.json)
* [ARTEFACT_GOLANG_PROJECT_INFO_FEDORA](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-project-info-fedora.json)
* [ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-ipprefix-to-package-name.json)

## Usage

```python
from infra.system.core.factory.functionfactory import FunctionFactory

function = FunctionFactory().bake("specdataextractor")
data = {
	"product": "Fedora",
	"distribution": "rawhide",
	"package": "golang-github-coreos-pkg",
	"resource": "/home/user/goproject"
}


artefacts = function.call(data)
```
