#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.listify import listify_lookup_plugin_terms
import StringIO
import gzip
import base64
import json


class FilterModule(object):

    @staticmethod
    def artefact2json(data):
        fd = StringIO.StringIO(base64.b64decode(data))
        gz = gzip.GzipFile(fileobj=fd, mode="r")
        js = gz.read()
        gz.close()
        fd.close()
        return json.loads(js)


    ''' Query filter '''

    def filters(self):
        return {
            'artefact2json': self.artefact2json,
        }
