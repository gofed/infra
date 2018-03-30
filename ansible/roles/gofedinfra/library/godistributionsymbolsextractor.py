#!/usr/bin/python

from ansible.module_utils.basic import *
from gofedlib.go.symbolsextractor import extractor
from gofedlib.types import ExtractionError
from gofedinfra.system.artefacts.artefacts import (
    ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
    ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API,
    ARTEFACT_GOLANG_IPPREFIX_TO_RPM,
)
from gofedlib.providers.providerbuilder import ProviderBuilder

from infra.system.helpers.artefactdecomposer import ArtefactDecomposer
from gofedlib.go.importpath.parserbuilder import ImportPathParserBuilder


class GoDistributionSymbolsExtractor(object):

    def __init__(self, directory, product="", distribution="", build="", rpm="", hexsha=""):
        self._directory = directory
        self._product = product
        self._distribution = distribution
        self._build = build
        self._rpm = rpm
        self._hexsha = hexsha

        self._packages = []
        self._exported_api = []
        self._mappings = []

    def extract(self):
        e = extractor.GoSymbolsExtractor(
            self._directory,
        )
        e.extract()

        self._packages = self._generateGolangProjectDistributionPackages(e.packages())
        self._exported_api = self._generateGolangProjectDistributionExportedAPI(e.exportedApi())
        self._mappings = self._generateGolangIpprefixToRpm(self._packages)

    def _generateGolangProjectDistributionPackages(self, packages):
        artefact = {
            "artefact": ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
            "commit": self._hexsha,
            "product": self._product,
            "distribution": self._distribution,
            "rpm": self._rpm,
            "build": self._build,
            "data": packages,
        }

        return ArtefactDecomposer(ImportPathParserBuilder().buildDefault()).decomposeArtefact(artefact)

    def _generateGolangProjectDistributionExportedAPI(self, exported_api):
        artefact = {
            "artefact": ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API,
            "product": self._product,
            "distribution": self._distribution,
            "rpm": self._rpm,
            "build": self._build,
            "commit": self._hexsha,
            "packages": exported_api,
        }

        return ArtefactDecomposer(ImportPathParserBuilder().buildDefault()).decomposeArtefact(artefact)

    def _generateGolangIpprefixToRpm(self, distro_packages):
        mappings = []
        for item in distro_packages["data"]:
            # TODO(jchaloup): add architecture to the artefact and make it part of its key
            mappings.append({
               "artefact": ARTEFACT_GOLANG_IPPREFIX_TO_RPM,
               "ipprefix": item["ipprefix"],
               "commit": self._hexsha,
               "rpm": self._rpm,
               "product": self._product,
               "distribution": self._distribution,
               "build": self._build
           })

        return mappings

    def golangProjectDistributionPackagesArtefact(self):
        return self._packages

    def golangProjectDistributionExportedAPI(self):
        return self._exported_api

    def golangIpprefixToRpm(self):
        return self._mappings


def main():

    fields = {
        "directory": {"required": True, "type": "str"},
        "product": {"required": False, "type": "str", "default": ""},
        "distribution": {"required": False, "type": "str", "default": ""},
        "build": {"required": False, "type": "str", "default": ""},
        "rpm": {"required": False, "type": "str", "default": ""},
        "hexsha": {"required": False, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields)

    e = GoDistributionSymbolsExtractor(
        module.params["directory"],
        product=module.params["product"],
        distribution=module.params["distribution"],
        build=module.params["build"],
        rpm=module.params["rpm"],
        hexsha=module.params["hexsha"],
    )
    failed = False
    errmsg = ""

    try:
        e.extract()
    except ExtractionError as err:
        failed = True
        errmsg = err
    except OSError as err:
        failed = True
        errmsg = err

    result = dict(
        product=module.params["product"],
        distribution=module.params["distribution"],
        build=module.params["build"],
        rpm=module.params["rpm"],
        hexsha=module.params["hexsha"],
        artefacts={
            ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES: e.golangProjectDistributionPackagesArtefact(),
            ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API: e.golangProjectDistributionExportedAPI(),
            ARTEFACT_GOLANG_IPPREFIX_TO_RPM: e.golangIpprefixToRpm(),
        },
        changed=True,
    )

    if failed:
        module.fail_json(msg=errmsg, **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
