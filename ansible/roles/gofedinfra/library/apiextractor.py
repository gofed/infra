#!/usr/bin/python

from ansible.module_utils.basic import *
from gofedlib.go.apiextractor import extractor
from gofedlib.providers.providerbuilder import ProviderBuilder
from gofedlib.go.snapshot import Snapshot
import json
import StringIO
import gzip
import base64

from gofedinfra.system.artefacts.artefacts import (
    ARTEFACT_GOLANG_PROJECT_API,
    ARTEFACT_GOLANG_PROJECT_STATIC_ALLOCATIONS,
    ARTEFACT_GOLANG_PROJECT_CONTRACTS
)


class ApiExtractor(object):

    def __init__(self, gopath, generated, package_path, hexsha, depsfile, goversion, artefact_prefix, artefact_key, cgodir=""):
        self._extractor = extractor.ApiExtractor(
            gopath, generated, package_path, hexsha, depsfile, goversion, cgodir)
        self._generated = generated
        self._api_artefacts = []
        self._contract_artefacts = []
        self._static_alloc_artefacts = []
        self._artefact_prefix = artefact_prefix
        self._artefact_key = artefact_key

        self._package_path = package_path
        self._snapshot = Snapshot()
        self._snapshot.clear()
        # Detect the snapshot type based on file name
        if depsfile.endswith("Godeps.json"):
            self._snapshot.readGodepsFile(depsfile)
            return
        if depsfile.endswith("glide.lock"):
            self._snapshot.readGlideLockFile(depsfile)
            return
        if depsfile.endswith("Glogfile"):
            self._snapshot.readGLOGFILE(depsfile)
            return
        raise ValueError("Dependency file format not recognized")

    def extract(self):
        self._extractor.extract()
        self._generateArtefacts()
        return self

    def _dict2gzip(self, dict):
        fd = StringIO.StringIO()
        gz = gzip.GzipFile(fileobj=fd, mode="w")
        gz.write(json.dumps(dict))
        gz.close()
        data = fd.getvalue()
        fd.close()
        return base64.b64encode(data)

    def _generateArtefacts(self):
        self._api_artefacts = []
        self._contract_artefacts = []
        self._static_alloc_artefacts = []
        up = ProviderBuilder().buildUpstreamWithLocalMapping()
        gl = len(self._generated)

        packages = self._snapshot.packages()

        for root, dirs, files in os.walk(self._generated):
            if root.startswith(os.path.join(self._generated, "golang/")):
                continue

            # TODO(jchaloup): generate artefacts in parallel
            for file in filter(lambda f: f.endswith(".json"), files):
                if file != "contracts.json" and file != "api.json" and file != "allocated.json":
                    continue

                ipp_hexsha = root[gl + 1:]
                hexsha = os.path.basename(ipp_hexsha)
                ipprefix = os.path.dirname(ipp_hexsha)
                with open(os.path.join(root, file), "r") as fp:
                    data = json.load(fp)

                artefact = {
                    # Repository of origin
                    "project": up.parse(ipprefix).prefix(),
                    "data": self._dict2gzip(data),
                    "ipprefix": ipprefix,
                }

                # All artefacts of project dependencies are generated from upstream commits
                # and they correspond to golang-project namespace.
                # So the artefact key can be applied only on the project itself.
                if ipprefix.startswith(self._package_path):
                    artefact_prefix = self._artefact_prefix
                    for key in self._artefact_key:
                        artefact[key] = self._artefact_key[key]
                else:
                    artefact_prefix = "golang-project"
                    try:
                        artefact["hexsha"] = packages[ipprefix]
                    except KeyError:
                        # Package not found => do not generate the artefact
                        continue


                if file == "api.json":
                    # The list of all packages for a given project is
                    # stored in golang-project-packages artefact
                    # So it's ok to use the ipprefix as a part of the api artefact key
                    artefact["artefact"] = "{}-api".format(artefact_prefix)
                    self._api_artefacts.append(artefact)
                    continue

                if file == "contracts.json":
                    artefact["artefact"] = "{}-contracts".format(artefact_prefix)
                    self._contract_artefacts.append(artefact)
                    continue

                if file == "allocated.json":
                    artefact["artefact"] = "{}-static-allocations".format(artefact_prefix)
                    self._static_alloc_artefacts.append(artefact)
                    continue

    def apiArtefacts(self):
        return self._api_artefacts

    def contractArtefacts(self):
        return self._contract_artefacts

    def statisAllocationArtefacts(self):
        return self._static_alloc_artefacts


def main():

    fields = {
        "gopath": {"required": True, "type": "str"},
        "generated": {"required": True, "type": "str"},
        "package_path": {"required": True, "type": "str"},
        "hexsha": {"required": True, "type": "str"},
        "depsfile": {"required": True, "type": "str"},
        "cgodir": {"required": False, "type": "str", "default": ""},
        "goversion": {"required": True, "type": "str"},
        "artefact": {"required": True, "type": "dict"},
    }

    module = AnsibleModule(argument_spec=fields)

    if "prefix" not in module.params["artefact"]:
        module.fail_json(msg="artefact argument missing prefix field")

    if "key" not in module.params["artefact"]:
        module.fail_json(msg="artefact argument missing key field")

    if type({}) != type(module.params["artefact"]["key"]):
        module.fail_json(msg="artefact.key field is not a dictionary")

    for key in module.params["artefact"]["key"]:
        if type("") != type(module.params["artefact"]["key"][key]):
            module.fail_json(msg="artefact.key is not a simple dictionary")

    e = ApiExtractor(
        gopath=module.params["gopath"],
        generated=module.params["generated"],
        package_path=module.params["package_path"],
        hexsha=module.params["hexsha"],
        depsfile=module.params["depsfile"],
        cgodir=module.params["cgodir"],
        goversion=module.params["goversion"],
        artefact_prefix=module.params["artefact"]["prefix"],
        artefact_key=module.params["artefact"]["key"],
    )

    failed = False
    errmsg = ""

    try:
        e.extract()
    except extractor.ExtractionException as err:
        failed = True
        errmsg = err

    result = dict(
        package_path=module.params["package_path"],
        hexsha=module.params["hexsha"],
        artefacts={
            "{}-api".format(module.params["artefact"]["prefix"]): e.apiArtefacts(),
            "{}-contracts".format(module.params["artefact"]["prefix"]): e.contractArtefacts(),
            "{}-static-allocations".format(module.params["artefact"]["prefix"]): e.statisAllocationArtefacts(),
        },
        changed=True,
    )

    if failed:
        module.fail_json(msg=errmsg, **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
