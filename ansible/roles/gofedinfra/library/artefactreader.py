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
        "repository": {"required": False, "type": "str"},
        "hexsha": {"required": False, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields)

    failed = False
    errmsg = ""
    artefact = {}

    key = {
        "artefact": module.params["artefact"],
    }

    if "repository" in module.params:
        key["repository"] = ProviderBuilder().buildUpstreamWithLocalMapping().parse(module.params["repository"]).signature()

    if "hexsha" in module.params:
        key["commit"] = module.params["hexsha"]

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
