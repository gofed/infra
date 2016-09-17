# Go API diff

Compare API of two projects.
The analyzer provides:

* a list of new/updated/removed packages
* a list of new/updated/removed functions/variables/datatypes for each updated package

## Input schema

* [input_schema.json](https://github.com/gofed/infra/blob/master/system/plugins/goapidiff/input_schema.json)

E.g.

```json
{
	"exported_api_1": "exported_api1_artefact",
	"exported_api_2": "exported_api2_artefact"
}
```

## Provided artefacts

* [ARTEFACT_GOLANG_PROJECT_API_DIFF](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-projects-api-diff.json)

## Usage

```python
from infra.system.core.factory.functionfactory import FunctionFactory

function = FunctionFactory().bake("gosymbolsextractor")
data1 = {
	"resource": "/home/user/goproject",
	"project": "github.com/onsi/ginkgo",
	"commit": "105b4823ee2cbebc2b5c562d9ac50694ecc2c689",
	"ipprefix": "github.com/onsi/ginkgo"
}

data2 = {
	"resource": "/home/user/goproject",
	"project": "github.com/onsi/ginkgo",
	"commit": "a0fde42296592b3bee4503370464b5789cf83440",
	"ipprefix": "github.com/onsi/ginkgo"
}

artefacts1 = function.call(data1)
artefacts2 = function.call(data2)

// retrieve api from artefact1 and artefact2
for artefact in artefact1:
	if artefact["artefact"] == "golang-project-exported-api":
		exported_api1 = artefact

for artefact in artefact2:
	if artefact["artefact"] == "golang-project-exported-api":
		exported_api2 = artefact

data = {
	"exported_api_1": exported_api1,
	"exported_api_2": exported_api2
}

analyzer = FunctionFactory().bake("goapidiff")

artefact = analyzer.call(artefact)
```

