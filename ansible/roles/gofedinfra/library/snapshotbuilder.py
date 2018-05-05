#!/usr/bin/python

from ansible.module_utils.basic import *
from gofedlib.go.snapshot import Snapshot
from gofedlib.providers.providerbuilder import ProviderBuilder

class SnapshotBuilder(object):

    def __init__(self, snapshotfile):
        self._snapshotfile = snapshotfile
        self._snapshot = Snapshot()
        self._providers = {}

    def parse(self):
        self._snapshot.clear()
        # Detect the snapshot type based on file name
        if self._snapshotfile.endswith("Godeps.json"):
            self._snapshot.readGodepsFile(self._snapshotfile)
            return self
        if self._snapshotfile.endswith("glide.lock"):
            self._snapshot.readGlideLockFile(self._snapshotfile)
            return self
        if self._snapshotfile.endswith("Glogfile"):
            self._snapshot.readGLOGFILE(self._snapshotfile)
            return self
        raise ValueError("File format not recognized")

    def packages(self):
        return self._snapshot.packages()

    def classes(self):
        return self._snapshot.classes()

    def providers(self):
        return self._providers

    def project2provider(self):
        up = ProviderBuilder().buildUpstreamWithLocalMapping()
        classes = self._snapshot.classes()
        for key in classes:
            self._providers[up.parse(key).prefix()] = classes[key]
        return self


def main():

    fields = {
        "snapshotfile": {"required": True, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields)

    failed = False
    errmsg = ""
    artefact = {}

    try:
        snapshot = SnapshotBuilder(module.params["snapshotfile"]).parse().project2provider()
        artefact = {
            "artefact": "golang-dependency-snapshot",
            "packages": snapshot.packages(),
            "classes": snapshot.classes(),
            "providers": snapshot.providers(),
        }
    except ValueError as err:
        failed = True
        errmsg = err
    except KeyError as err:
        failed = True
        errmsg = err

    result = dict(
        artefact=artefact,
        changed=True,
        error=errmsg,
    )

    if failed:
        result["found"] = False

    module.exit_json(**result)


if __name__ == '__main__':
    main()
