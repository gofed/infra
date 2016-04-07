# Go distribution symbols extractor

Extractor aimed at distribution rpms.
The plugin is extensition of [Go symbols extractor](https://github.com/gofed/infra/tree/master/system/plugins/gosymbolsextractor).
As one rpm can ship more source code units with different import path prefixes,
each artefact carrying information about source code is decomposed by prefix.

## Input schema

* [input_schema.json](https://github.com/gofed/infra/blob/master/system/plugins/distributiongosymbolsextractor/input_schema.json)

E.g.

```json
{
	"product": "Fedora",
	"distribution": "rawhide",
	"build": "etcd-2.3.1-1.fc25",
	"rpm": "etcd-devel-2.3.1-1.fc25.noarch.rpm",
	"resource": "/home/user/rpmlocation",
	"commit": "b137df77f11674267af984beed86d8a32c737a6b"
}
```

## Provided artefacts

* [ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-project-distribution-packages.json)
* [ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-project-distribution-exported-api.json)

## Usage

```python
from infra.system.core.factory.functionfactory import FunctionFactory

function = FunctionFactory().bake("distributiongosymbolsextractor")
data = {
	"product": "Fedora",
	"distribution": "rawhide",
	"build": "etcd-2.3.1-1.fc25",
	"etcd-devel-2.3.1-1.fc25.noarch.rpm",
	"resource": "/home/user/rpmlocation",
	"commit": "b137df77f11674267af984beed86d8a32c737a6b"
}

artefacts = function.call(data)
```
