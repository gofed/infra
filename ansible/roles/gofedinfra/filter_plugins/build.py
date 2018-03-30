#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.listify import listify_lookup_plugin_terms
from gofedlib.distribution.helpers import Build, Rpm


class FilterModule(object):

    @staticmethod
    def rpmname(name, build):
        return Rpm(build, name).name()

    @staticmethod
    def rpmarch(name, build):
        return Rpm(build, name).arch()

    @staticmethod
    def package(build):
        return Build(build).name()


    ''' Query filter '''

    def filters(self):
        return {
            'rpmname': self.rpmname,
            'rpmarch': self.rpmarch,
            'packagename': self.package,
        }
