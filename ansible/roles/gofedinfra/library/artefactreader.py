#!/usr/bin/python

from ansible.module_utils.basic import *
import json
from gofedinfra.system.core.meta.metastoragereader import MetaStorageReader
from gofedinfra.system.plugins.simplefilestorage.artefactdriverfactory import ArtefactDriverFactory
from gofedlib.providers.providerbuilder import ProviderBuilder

class StorageReader(MetaStorageReader):

    def retrieve(self, data):
        """Retrieve artefact from storage

        param data: artefact key to retrieve
        type  data: dictionary
        """
        if "artefact" not in data:
            raise ValueError("artefact key not found in %s" % json.dumps(data))

        driver = ArtefactDriverFactory().build(data["artefact"])
        if driver == None:
            raise KeyError("artefact driver for %s not found" % data["artefact"])

        return driver.retrieve(data)


def main():

    fields = {
        "artefact": {"required": True, "type": "str"},
        "repository": {"required": False, "type": "str", "default": ""},
        "hexsha": {"required": False, "type": "str", "default": ""},
        "product": {"required": False, "type": "str", "default": ""},
        "distribution": {"required": False, "type": "str", "default": ""},
        "package": {"required": False, "type": "str", "default": ""},
        "build": {"required": False, "type": "str", "default": ""},
        "rpm": {"required": False, "type": "str", "default": ""},
    }

    module = AnsibleModule(argument_spec=fields)

    failed = False
    errmsg = ""
    artefact = {}

    key = {
        "artefact": module.params["artefact"],
    }

    for field in fields:
        if field == "repository":
            try:
                if module.params["repository"]:
                    key["repository"] = ProviderBuilder().buildUpstreamWithLocalMapping().parse(module.params["repository"]).signature()
            except KeyError:
                pass
            continue

        if field == "hexsha":
            try:
                if module.params["hexsha"]:
                    key["commit"] = module.params["hexsha"]
            except KeyError:
                pass
            continue

        if field in module.params:
            key[field] = module.params[field]

    try:
        artefact = StorageReader().retrieve(key)
    except ValueError as err:
        failed = True
        errmsg = err
    except KeyError as err:
        failed = True
        errmsg = err

    result = dict(
        artefact=artefact,
        changed=True,
        key=key,
        found=True,
    )

    if failed:
        result["found"] = False

    module.exit_json(**result)


if __name__ == '__main__':
    main()
