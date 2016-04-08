# Distribution package builds extractor

Extract basic information about builds of a given package.
Basic information covers:

* list of builds in a given date interval
* build info (name, author, build time, list of rpms, etc.) for each build in a given date interval

## Input schema

* [input_schema.json](https://github.com/gofed/infra/blob/master/system/plugins/distributionpackagebuildsextractor/input_schema.json)

E.g.

```json
{
	"package": "etcd",
	"product": "Fedora",
	"distribution": "f24",
	"start_timestamp": 1400131190,
	"end_timestamp": 1460131190
}
```

## Provided artefacts

* [ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-project-distribution-package-builds.json)
* [ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-project-distribution-build.json)

## Usage

```python
from infra.system.core.factory.functionfactory import FunctionFactory

function = FunctionFactory().bake("distributionpackagebuildsextractor")
data = {
	"package": "etcd",
	"product": "Fedora",
	"distribution": "f24",
	"start_timestamp": 1400131190,
	"end_timestamp": 1460131190
}

artefacts = function.call(data)
```
