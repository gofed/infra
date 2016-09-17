# Go symbols extractor

Extract definition of data types and functions.
Variables and constants are extracted as a list of IDs without their data type definition.
All source code files are processed separately. All extracted data are then merged together
to provide exported API for each golang package. As some variables and constants can be assigned
a value or their datatype can be build of types from other packages, the full data type definition
is not available.

The plugin is partially written in Go (parser part) and partially in Python (merger and filter part).

## Input schema

* [input_schema.json](https://github.com/gofed/infra/blob/master/system/plugins/gosymbolsextractor/input_schema.json)

E.g.

```json
{
	"resource": "/home/user/goproject",
	"project": "github.com/onsi/ginkgo",
	"commit": "105b4823ee2cbebc2b5c562d9ac50694ecc2c689",
	"ipprefix": "github.com/onsi/ginkgo"
}
```

## Provided artefacts

* [ARTEFACT_GOLANG_PROJECT_PACKAGES](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-project-packages.json)
* [ARTEFACT_GOLANG_PROJECT_EXPORTED_API](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-project-exported-api.json)

## Usage

```python
from infra.system.core.factory.functionfactory import FunctionFactory

function = FunctionFactory().bake("gosymbolsextractor")
data = {
	"resource": "/home/user/goproject",
	"project": "github.com/onsi/ginkgo",
	"commit": "105b4823ee2cbebc2b5c562d9ac50694ecc2c689",
	"ipprefix": "github.com/onsi/ginkgo"
}

artefacts = function.call(data)
```

## Limitations

* variables and constants are mixed together as constants
* variables and constants does not have data type definition
