from system.plugins.storages.metaartefactdriver import MetaArtefactDriver
from system.helpers.artefactkeygenerator.golang_ipprefix_to_package_name import GolangIPPrefixToPackageNameKeyGenerator
from etcdclient import EtcdClient
import json
import logging

ARTEFACT = "golang-ipprefix-to-package-name"

class GolangIPPrefixToPackageNameDriver(MetaArtefactDriver):

	def store(self, data):
		"""store artefact"""
		# generate key
		key = GolangIPPrefixToPackageNameKeyGenerator().generate(data)
		if key == "":
			logging.error("Unable to store %s artefact: key not generated" % ARTEFACT)
			return False

		# store the data into etcd
		if EtcdClient().set(key, json.dumps(data)):
			logging.error("Unable to store %s artefact with '%s' key" % (ARTEFACT, key))
			return False

		return True

	def retrieve(self, key_data):
		"""retrieve artefact"""
		key = GolangIPPrefixToPackageNameKeyGenerator().generate(key_data)
		if key == "":
			logging.error("Unable to store %s artefact: key not generated" % ARTEFACT) 
			return False

		# get the data from etcd
		ok, value = EtcdClient().get(key)

		if not ok:
			logging.error("Unable to retrieve %s artefact with '%s' key" % (ARTEFACT, key))
			return ""

		return value

	def storeList(self, dataList):
		"""store list of artefacts"""
		raise NotImplementedError

	def retrieveList(self, key):
		"""retrieve list of artefacts"""
		raise NotImplementedError

