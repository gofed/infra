# Ecosystem management

Carry actions required for keeping golang ecosystem in shape (healthy and vital).

Currently watched systems:

* distribution builds
* upstream projects

Run checks on the ecosystem to see what is not healthy and what is available:

* missing dependencies
* cyclic dependencies
* supported architectures
* deviation between upstream project and corresponding distribution rpms
* supported architectures for each project
* available golang projects in a distribution

Extended ecosystem scans can provide:

* difference in API of consequitive golang projects/distribution rpms
* allocated API of each project in a distribution

## Ecosystem maintainance

Two steps are taken:

1) fetch the current snapshot of the ecosystem
  * get latest builds in distributions
  * latest commits in upstream projects
  * scan latests builds and commits
2) run health check and analysis over scanned rpms/commits

## Fetchers

Fetch the current state of ecosystem in a form of snapshosts and list
of available builds/commits for each package/project.

Responsibility of each fetcher is to get a list of all available objects.
At the same time scan the latest instances of available objects.
Analyses over scanned instances is not in a scope of any fetcher.

E.g.:

* fetch new releases (with a list of bugfixes and other important information)
* fetch new issues (bugzilla, filtered upstream issues, etc.)
* fetch new builds (for each distribution)
* fetch new commits, and branches (of each project packages in at least one distribution)
* fetch new updates, overrides, review requests, etc.

## Watchers

Watch over ecosystem, report any unhealthy behaviour and check for news:

* report missing dependencies (projects)
* report updates not pushed to stable repository
* collect failing tests
* collect lint runs on spec files and report missing dependencies, provided packages, tests, etc.
* report limitations of projects, e.g. unsupported architectures, known defects, list of opened bugs

Daily/Weekly digest can be sent to registered user (e.g. mailing lists).

## Executors

Execute actions needed to change unhealthy ecosystem to healthy ecosystem:

* open bugzilla issues (missing dependencies, unhealthy spec file)
* send mails about current state of packages to individual maintainers or MLs
* open issues on github for each unhealthy project (only important issues)

## Workers

Run periodic actions over ecosystem to collect current state of the ecosytem health:

* periodically trigger unit-tests for each golang project packages in each distribution
* periodically run lint on all spec files
* periodically run available integration tests (and other non-unit tests)
* periodically run analysis of dependencies and collect distinctive artefacts (missing dependencies, cyclic dependencies, etc.)
* periodically run allocation analysis over packages (for each project make a list of API that is used) and report incompatibilities and missing symbols
