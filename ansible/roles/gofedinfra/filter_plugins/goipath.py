#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.listify import listify_lookup_plugin_terms
import yaml


class FilterModule(object):

    @staticmethod
    def hexsha(goipath):
        with open(goipath, "r") as f:
            d = yaml.load(f)
            return d["metadata"]["commit"]

    ''' Query filter '''

    def filters(self):
        return {
            'goipath2hexsha': self.hexsha,
        }
