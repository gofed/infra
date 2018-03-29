#!/usr/bin/python

from ansible.module_utils.basic import *
import time
import datetime

from gofedinfra.system.artefacts.artefacts import (
    ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD,
    ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS
)
from gofedlib.utils import generateDateCoverage
from gofedlib.distribution.clients.koji.client import KojiClient


class DistributionPackageBuildsExtractor(object):

    def __init__(self, product, distribution, package, since=int(time.mktime(datetime.datetime.strptime("2008-01", "%Y-%m").timetuple())), to=int(time.time()) + 86400, info={}):
        self._product = product
        self._distribution = distribution
        self._package = package
        self._current_info = info

        # Alter the since so it covers entire month
        if since != 0:
            dt = datetime.datetime.fromtimestamp(since)
            ditem = datetime.datetime.strptime(
                "{}-{}".format(dt.strftime("%Y"), dt.strftime("%m")), "%Y-%m")
            since = int(time.mktime(ditem.timetuple()))

        # Alter the to so it covers entire month
        todt = datetime.datetime.fromtimestamp(to)
        c_y = int(datetime.datetime.now().year)
        c_m = int(datetime.datetime.now().month)
        if todt.year >= c_y and todt.month >= c_m:
            to = int(time.time()) + 86400

        self._since = since
        self._to = to
        self._coverage = []

        self._info = {}
        self._builds = {}

    def extract(self):
        # detailed builds data
        builds_data = KojiClient().getPackageBuilds(
            self._distribution,
            self._package,
            since=self._since,
            to=self._to
        )

        # dict of builds in the info
        builds = {}
        # builds artefacts
        self._builds = {}

        # merge both infos
        if self._current_info:
            coverage = {}
            c_y = int(datetime.datetime.now().year)
            c_m = int(datetime.datetime.now().month)
            for item in self._current_info["coverage"] + generateDateCoverage(self._since, self._to):
                try:
                    ditem = datetime.datetime.strptime(item, "%Y-%m-%d %H:%M")
                    if ditem.year >= c_y and ditem.month >= c_m:
                        # The current date month so limit the upper bound by today
                        item = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    else:
                        # Older month => cover entire month
                        mprefix = ""
                        if ditem.month < 10:
                            mprefix = "0"
                        item = "{}-{}{}".format(ditem.year, mprefix, ditem.month)

                    # Extract missing info
                    y = int(ditem.year)
                    m = int(ditem.month)
                    since = int(time.mktime(datetime.datetime.strptime(
                        "{}-{}".format(y, m), "%Y-%m").timetuple()))
                    y += m / 12  # m-1 counting from 0, then + 1 and module 12 a.k.a (m-1+1)/12
                    m = (m + 1) % 12
                    to = int(time.mktime(datetime.datetime.strptime(
                        "{}-{}".format(y, m), "%Y-%m").timetuple()))

                    l_builds = KojiClient().getPackageBuilds(
                        self._distribution,
                        self._package,
                        since=self._since,
                        to=self._to
                    )

                    for b in l_builds:
                        builds_data[b] = l_builds[b]

                except ValueError:
                    ditem = datetime.datetime.strptime(item, "%Y-%m")

                y = int(ditem.year)
                m = int(ditem.month)
                if y not in coverage:
                    coverage[y] = {}
                if m not in coverage[y]:
                    coverage[y][m] = item

            # Mix the rest
            self._coverage = []
            for y in coverage:
                for m in coverage[y]:
                    self._coverage.append(coverage[y][m])

            # Mix builds
            builds = self._current_info["builds"]
        else:
            self._coverage = generateDateCoverage(self._since, self._to)

        self._coverage.sort(reverse=True)

        for build in builds_data:
            builds[build] = builds_data[build]["build_ts"]

            if build in self._builds:
                continue

            self._builds[build] = self._generateGolangProjectDistributionBuild(builds_data[build])

        self._info = self._generateGolangProjectDistributionPackageBuilds(builds)

        return self

    def _generateGolangProjectDistributionBuild(self, build):
        artefact = {}

        artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD
        artefact["product"] = self._product
        artefact["name"] = build['name']

        artefact["build_ts"] = build['build_ts']
        artefact["author"] = build['author']
        artefact["architectures"] = list(build['architectures'])
        artefact["rpms"] = build['rpms']
        artefact["build_url"] = "http://koji.fedoraproject.org/koji/buildinfo?buildID=" + \
            str(build['id'])

        return artefact

    def _generateGolangProjectDistributionPackageBuilds(self, builds):
        artefact = {}

        artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS

        artefact["package"] = self._package
        artefact["product"] = self._product
        artefact["distribution"] = self._distribution
        artefact["builds"] = builds

        artefact["coverage"] = self._coverage

        return artefact

    def golangProjectDistributionPackageBuilds(self):
        return self._info

    def golangProjectDistributionBuilds(self):
        return self._builds


def main():

    fields = {
        "package": {"required": True, "type": "str"},
        "distribution": {"required": True, "type": "str"},
        "product": {"required": False, "type": "str", "default": ""},
        "info": {"required": False, "type": "dict"},
        "from_ts": {"required": False, "type": "str"},
        "from_date": {"required": False, "type": "str"},
        "to_ts": {"required": False, "type": "str"},
        "to_date": {"required": False, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields)

    if module.params["from_ts"]:
        from_ts = int(module.params["from_ts"])
    elif module.params["from_date"]:
        from_ts = int(time.mktime(datetime.datetime.strptime(
            module.params["from_date"], "%Y-%m-%d").timetuple()))
    else:
        from_ts = int(time.mktime(datetime.datetime.strptime("2008-01", "%Y-%m").timetuple()))

    if module.params["to_ts"]:
        to_ts = int(module.params["to_ts"])
    elif module.params["to_date"]:
        to_ts = int(time.mktime(datetime.datetime.strptime(
            module.params["to_date"], "%Y-%m-%d").timetuple()))
    else:
        to_ts = int(time.time())

    e = DistributionPackageBuildsExtractor(
        package=module.params["package"],
        distribution=module.params["distribution"],
        product=module.params["product"],
        since=from_ts,
        to=to_ts,
        info=module.params["info"],
    )

    e.extract()

    result = dict(
        changed=True,
        covered=True,
        since=from_ts,
        to=to_ts,
        artefacts={
            ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD: e.golangProjectDistributionBuilds(),
            ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS: e.golangProjectDistributionPackageBuilds(),
        }
    )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
