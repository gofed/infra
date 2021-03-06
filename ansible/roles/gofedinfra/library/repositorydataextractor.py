#!/usr/bin/python

from ansible.module_utils.basic import *
import time
import datetime

from gofedlib.repository.repositoryclientbuilder import RepositoryClientBuilder
from gofedlib.providers.providerbuilder import ProviderBuilder
from gofedinfra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO, ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT
from gofedlib.utils import generateDateCoverage

class RepositoryDataExtractor(object):

    def __init__(self, directory, repository="", hexsha="", branch="", since=int(time.mktime(datetime.datetime.strptime("2008-01", "%Y-%m").timetuple())), to=int(time.time()) + 86400, info={}):
        self._directory = directory

        provider = ProviderBuilder().buildUpstreamWithLocalMapping()
        provider.parse(repository)

        self._repository = provider.signature()
        self._hexsha = hexsha
        self._branch = branch
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
        self._commits = {}

    def extract(self):
        repo_client = RepositoryClientBuilder().buildWithLocalClient(
            self._repository, self._directory)

        # just a single commit
        if self._hexsha:
            self._commits[self._hexsha] = self._generateGolangProjectRepositoryCommit(
                repo_client.commit(self._hexsha)
            )
            return self

        all_branches = repo_client.branches()
        branched_commits = {}

        # just a single branch
        if self._branch != "":
            if self._branch not in all_branches:
                raise ValueError("Requested branch '%s' not found" % self.branch)

            branched_commits[self._branch] = repo_client.commits(
                self._branch,
                since=self._since,
                to=self._to,
            )
            return self

        # all branches
        for branch in all_branches:
            branched_commits[branch] = repo_client.commits(
                branch,
                since=self._since,
                to=self._to,
            )

        self._commits = {}
        branches = {}

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

                    for branch in all_branches:
                        l_commits = repo_client.commits(branch, since=since, to=to)
                        for c in l_commits:
                            try:
                                branched_commits[branch][c] = l_commits[c]
                            except KeyError:
                                branched_commits[branch] = {}
                                branched_commits[branch][c] = l_commits[c]

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

            # Mix branches
            for item in self._current_info["branches"]:
                branches[item["branch"]] = item["commits"]
        else:
            self._coverage = generateDateCoverage(self._since, self._to)

        self._coverage.sort(reverse=True)

        for branch in branched_commits:
            for commit in branched_commits[branch]:
                try:
                    branches[branch][commit] = branched_commits[branch][commit]["cdate"]
                except KeyError:
                    branches[branch] = {}
                    branches[branch][commit] = branched_commits[branch][commit]["cdate"]

                if commit in self._commits:
                    continue

                self._commits[commit] = self._generateGolangProjectRepositoryCommit(
                    branched_commits[branch][commit])

        # from all branches (up to master) filter out all commits that are already covered in master branch
        if "master" in branches:
            for branch in filter(lambda l: l != "master", branches.keys()):
                for key in branches["master"].keys():
                    branches[branch].pop(key, None)

        self._info = self._generateGolangProjectRepositoryInfo(branches)

        return self

    def _generateGolangProjectRepositoryCommit(self, commit):
        data = {}

        data['artefact'] = ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT
        data['repository'] = self._repository
        data['commit'] = commit["hexsha"]

        # keep timestamps
        data['adate'] = commit["adate"]
        data['cdate'] = commit["cdate"]
        data['author'] = commit["author"]
        data['message'] = commit["message"]

        return data

    def _generateGolangProjectRepositoryInfo(self, branches):
        data = {
            "artefact": ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO,
            "repository": self._repository,
            "branches": []
        }

        for branch in branches:
            data["branches"].append({
                "branch": branch,
                "commits": branches[branch]
            })

        data["coverage"] = self._coverage

        return data

    def golangProjectRepositoryInfo(self):
        return self._info

    def golangProjectRepositoryCommits(self):
        return self._commits


def main():

    fields = {
        "directory": {"required": True, "type": "str"},
        "repository": {"required": True, "type": "str"},
        "info": {"required": False, "type": "dict"},
        "from_ts": {"required": False, "type": "str"},
        "from_date": {"required": False, "type": "str"},
        "to_ts": {"required": False, "type": "str"},
        "to_date": {"required": False, "type": "str"},
        "hexsha": {"required": False, "type": "str"},
        "branch": {"required": False, "type": "str"},
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

    e = RepositoryDataExtractor(
        directory=module.params["directory"],
        repository=module.params["repository"],
        since=from_ts,
        to=to_ts,
        info=module.params["info"],
        hexsha=module.params["hexsha"],
    )

    e.extract()

    result = dict(
        changed=True,
        covered=True,
        since=from_ts,
        to=to_ts,
        artefacts={
            ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO: e.golangProjectRepositoryInfo(),
            ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT: e.golangProjectRepositoryCommits(),
        }
    )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
