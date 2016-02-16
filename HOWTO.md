## Running python code

From root directory run:

```vim
PYTHONPATH=$(pwd)/third_party python test.py
```

## Integrating new plugin

1. create new directory under ``/system/plugins``, e.g. ``/system/plugins/PLUGIN``
2. create ``register.json`` in ``/system/plugins/PLUGIN``

```json
{
"id": "plugin-id",
"class": "PluginClass",
"file": "pluginclassfile.py",
"version": "1.0-alpha1"
}
```
E.g.

```json
{
"id": "goapidiff",
"class": "GoApiDiff",
"file": "analyzer.py",
"version": "1.0-alpha1"
}
```
3. If the plugin generates new artefacts not yet available in the system, add all new artefacts into ``/system/artefacts/artefacts.py``. Then, update ``/generators/artefacts.json``. 

```json
{
        "id": "golang-project-api-diff",
        "artefact": "ARTEFACT_GOLANG_PROJECTS_API_DIFF",
        "keys": ["artefact", "project", "commit1", "commit2"]
}
```
Be aware, ``id`` is artefact id, not plugin id as in the ``register.json``.
At the same time ``artefact`` must have the same value is in ``/system/artefacts/artefacts.py``.

Once ``artefacts.json`` is updated, regenerate artefact key generators and drivers by running:

```
$ python generators/artefactdrivers.py
$ python generators/artefactkeys.py
```
