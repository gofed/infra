## Go symbols extractor

### Description

``Go symbols extractor`` plugin extracts definition of data types and functions.
Variables and constants are extracted as a list of IDs without their data type definition.
All source code files are processed separately. All extracted data are then merged together
to provide exported API for each golang package. As some variables and constants can be assigned
a value or their datatype can be build of types from other packages, the full data type definition
is not available.

The plugin is partially written in Go (parser part) and partially in Python (merger and filter part).

### Plugin input

```vim
{
"source_code_directory": "string",
"directories_to_skip": ["string"],
"project": "string",
"commit": "string",
"ipprefix": "string"
}
```

[input_schema.json](input_schema.json)

### Produced artefacts

* [golang-project-packages](/system/artefacts/schemas/golang-project-packages.json)
* [golang-project-exported-api](/system/artefacts/schemas/golang-project-exported-api.json)

#### Limitations

* variables and constants are mixed together as constants
* variables and constants does not have data type definition
