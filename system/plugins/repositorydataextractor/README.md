# Repository data extractor

Extract basic information about a repository:

* list of branches
* list of commits
* basic information for each commit, e.g. commit date, commit hexsha, commit message

Optionally, extract information about a single commit.

Currently supported revision systems:

* git (github.com)
* mercurial (bitbucket.org)

## Input schema

* [input_schema.json](https://github.com/gofed/infra/blob/master/system/plugins/repositorydataextractor/input_schema.json)

E.g.

```
{
	"repository": {
		"provider": "bitbucket",
		"username": "ww",
		"project": "goautoneg"
	},
	"resource": "/home/user/goproject",
	"start_date": "2016-03-01",
	"end_date": "2016-04-05"
}
```

## Provided artefacts

* [ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-project-repository-info.json)
* [ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT](https://github.com/gofed/infra/blob/master/system/artefacts/schemas/golang-project-repository-commit.json)

## Usage

```python
from infra.system.core.factory.functionfactory import FunctionFactory

function = FunctionFactory().bake("specdataextractor")
data = {
	"repository": {
		"provider": "bitbucket",
		"username": "ww",
		"project": "goautoneg"
	},
	"resource": "/home/user/goproject",
	"start_date": "2016-03-01",
	"end_date": "2016-04-05"
}

artefacts = function.call(data)
```
