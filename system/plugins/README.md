## How to write a plugin

**Requirements**:

* Make a list of artefacts plugin produces
* Define JSON Schema for all new artefacts
* Define JSON Schema for plugin's input
* Verify input and produced artefacts againts schemas
* Plugin always returns a list of artefacts

Each plugin must implement MetaProcessor from system.core.meta.metaprocessor.

