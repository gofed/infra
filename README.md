# Gofed infrastructure

[![Build Status](https://travis-ci.org/gofed/infra.svg?branch=master)](https://travis-ci.org/gofed/infra)

Infrastructure for gofed tool and various models built over data extracted from golang source codes.

It is designed to provide:

* general interface for integration of already existing plugins
* general interface to build acts (sequence of actions over integrated plugins)
* abstract way to declare resources that plugins work with

## Concepts

**Plugins**: building blocks integrating working pieces of a code (analysis, extractions, etc.) into the infrastructure

**Acts**: composition of actions providing data for your application, e.g. data needed to generate spec file, analysis of source code, dependency graph construction.

**Resource Handling**: declare what resource you want to work with and let the infrastructure retrieve the resource and provide it to a plugin.

**Action Handling**: once a plugin is integrated into the infrastructure it automatically gets an ID you can use to run the plugin.

## Requirements

* python2.7 (see [requirements.txt](requirements.txt))
* etcd

## How to start

The infrastructure is under construction atm. To try it you can run:

```vim
$ PYTHONPATH=$(pwd)/third_party:$(pwd)/../ python testact.py
```

The script is set to inspect code of ``github.com/bradfitz/http2`` of ``f8202bc903bda493ebba4aa54922d78430c2c42f`` commit.
Product of the run are two artefacts (json containing extracted data): ``golang-project-packages`` and ``golang-project-content-metadata``.
See [schemas](system/artefacts/schemas) for definition of artefacts.

## How to contribute

Although the infrastructure is not fully functional you can already create your own acts and integrate plugins.
At the moment we are concentrating on ecosystem analysis (scan of available builds and upstream project in question) to collect data about the ecosystem
and to prepare for its healh check. At the same time to provide better tooling and expose full experience with gofed tool.

Some issues can be found at [gofed/gofed](https://github.com/gofed/gofed/issues). Other are on a private board atm.
For more information contact jchaloup@redhat.com.

## Design principles

* never call Ansible inside an Ansible (all the Ansible logs should be generated by a single run, no nesting)

## TODO

* set ANSIBLE_CONFIG to point to the ansible/ansible.cfg  when running the gofed command (otherwise the gofedinfra role is not found)
* tests:
  * Ansible module level testing
  * Ansible role level testing later (as part of the Ansible module level testing, via Molecule?)
  * Ansible playbook level testing (start with online testing -> just run all the playbooks in a loop, one Ansible playbook running all entry points)
  * Model level testing (on top of a testing data corpus)
* Make playbook entry points, all the rest under private directory
* integrate the new go symbols extractor, replace the current gosymbolsextractor
* generate data corpus with allocated symbols (clear the previous one) as a timestamped tarball
