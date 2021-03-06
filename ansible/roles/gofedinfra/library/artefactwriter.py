#!/usr/bin/python

from ansible.module_utils.basic import *
import json
from gofedinfra.system.core.meta.metastoragewriter import MetaStorageWriter
from gofedinfra.system.plugins.simplefilestorage.artefactdriverfactory import ArtefactDriverFactory


class StorageWriter(MetaStorageWriter):

    def store(self, data):
        """Store artefact into storage

        param data: artefact writable to storage
        type  data: dictionary
        """
        if "artefact" not in data:
            raise KeyError("artefact key not found in %s" % json.dumps(data))

        return ArtefactDriverFactory().build(data["artefact"]).store(data)

def main():

    fields = {
        "artefact": {"required": True, "type": "dict"},
    }

    module = AnsibleModule(argument_spec=fields)

    failed = False
    errmsg = ""
    artefact_at = ""

    try:
        artefact_at = StorageWriter().store(module.params["artefact"])
    except ValueError as err:
        failed = True
        errmsg = err
    except KeyError as err:
        failed = True
        errmsg = err

    result = dict(
        artefact_at=artefact_at,
        stored=True,
    )

    if failed:
        result["stored"] = False
        module.fail_json(msg=errmsg, **result)
    else:
        result["changed"] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
