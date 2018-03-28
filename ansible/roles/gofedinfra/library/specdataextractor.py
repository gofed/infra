#!/usr/bin/python

from ansible.module_utils.basic import *
from gofedinfra.system.plugins.specdataextractor.SpecParser import SpecParser
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME,
	ARTEFACT_GOLANG_PROJECT_INFO_FEDORA,
	ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME
)
from datetime import datetime

class SpecDataExtractor(object):

    def __init__(self, specfile, product="", distribution="", package=""):
        self._specfile = specfile
        self._product = product
        self._distribution = distribution
        self._package = package

        self._commit = ""
        self._ipprefix = ""
        self._project = ""
        self._lastupdated = ""

    def extract(self):
        sp = SpecParser(self._specfile).parse()

        ##############################
        ##           COMMIT         ##
        ##############################
        # usually %commit is found
        self._commit = sp.getMacro("commit")
        # if the version is set, the %gcommit is assumed to exist
        if self._commit == "":
            self._commit = sp.getMacro("gcommit")
        # in some cases it can be even %rev but %[g]commit should be used instead
        if self._commit == "":
            self._commit = sp.getMacro("rev")
        # Not found, hups
        if self._commit == "":
            raise ValueError("commit/rev not found")
        ##############################
        ##          IPPREFIX        ##
        ##############################
        # Currentl expected value stored under goipath
        self._ipprefix = sp.getMacro("goipath")
        # Old specs sets import_path macro
        if self._ipprefix == "":
            self._ipprefix = sp.getMacro("import_path")
        if self._ipprefix == "":
            self._ipprefix = sp.getMacro("gobaseipath")
        # Not found, hups
        if self._ipprefix == "":
            raise ValueError("import path prefix not found")
        ##############################
        ##          PROVIDER        ##
        ##############################
        # Currently expected macro with the provider url is forgeurl
        self._project = sp.getMacro("forgeurl")
        # Older spec files still contains provider_prefix macro
        if self._project == "":
            self._project = sp.getMacro("provider_prefix")
        # Not set => use ipprefix
        if self._project == "":
            self._project = self._ipprefix

        # Extract date from changelog and set its format
        header = sp.getLastChangelog().header
        if header == "":
            raise ValueError("last changelog not found")
        try:
            # TODO(jchaloup): preprocess the line before converting to date
            date_data = re.sub(r' +', ' ', header.split('-')[0])
            date_data = " ".join(date_data.split(" ")[:5])
            self._lastupdated = datetime.strptime(date_data,"* %a %b %d %Y").strftime("%Y-%m-%d")
        except ValueError as e:
            raise ValueError("invalid changelog header format: {}".format(e))

    def golangProjectInfoFedora(self):
        return {
            "artefact": ARTEFACT_GOLANG_PROJECT_INFO_FEDORA,
            "distribution": self._distribution,
            "project": self._project,
            "commit": self._commit,
            "last-updated": self._lastupdated,
        }

    def golangProjectToPackageName(self):
        return {
            "artefact": ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME,
            "product": self._product,
            "distribution": self._distribution,
            "project": self._project,
            "name": self._package,
        }

    def golangIPPrefixToPackageName(self):
        return {
            "artefact": ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME,
            "product": self._product,
            "distribution": self._distribution,
            "ipprefix": self._ipprefix,
            "name": self._package,
        }

def main():

    fields = {
        "specfile": {"required": True, "type": "str"},
        "product": {"required": False, "type": "str", "default": ""},
        "distribution": {"required": False, "type": "str", "default": ""},
        "package": {"required": False, "type": "str", "default": ""},
    }

    module = AnsibleModule(argument_spec=fields)

    e = SpecDataExtractor(
        specfile=module.params["specfile"],
        product=module.params["product"],
        distribution=module.params["distribution"],
        package=module.params["package"],
    )

    failed = False
    errmsg = ""

    try:
        e.extract()
    except ValueError as err:
        failed = True
        errmsg = err

    result = dict(
        product=module.params["product"],
        distribution=module.params["distribution"],
        package=module.params["package"],
        artefacts={
            ARTEFACT_GOLANG_PROJECT_INFO_FEDORA: e.golangProjectInfoFedora(),
            ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME: e.golangProjectToPackageName(),
            ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME: e.golangIPPrefixToPackageName(),
        },
        changed=True,
    )

    if failed:
        module.fail_json(msg=errmsg, **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
