from system.plugins.storages.metaartefactdriver import MetaArtefactDriver
from system.helpers.artefactkeygenerator.golang_project_exported_api import GolangProjectExportedAPIKeyGenerator
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_EXPORTED_API
from etcdclient import EtcdClient
import json
import logging

class GolangProjectExportedAPIDriver(MetaArtefactDriver):

	def store(self, data):
		"""store artefact"""
		# generate key
		key = GolangProjectExportedAPIKeyGenerator().generate(data)
		if key == "":
			logging.error("Unable to store %s artefact: key not generated" % ARTEFACT_GOLANG_PROJECT_EXPORTED_API)
			return False

		# store the data into etcd
		if EtcdClient().set(key, json.dumps(data)):
			logging.error("Unable to store %s artefact with '%s' key" % (ARTEFACT_GOLANG_PROJECT_EXPORTED_API, key))
			return False

		return True

	def retrieve(self, key_data):
		"""retrieve artefact"""
		key = GolangProjectInfoFedoraKeyGenerator().generate(key_data)
		if key == "":
			logging.error("Unable to store %s: key not generated" % ARTEFACT_GOLANG_PROJECT_EXPORTED_API)
			return False

		# get the data from etcd
		ok, value = EtcdClient().get(key)

		if not ok:
			logging.error("Unable to retrieve %s artefact with '%s' key" % (ARTEFACT_GOLANG_PROJECT_EXPORTED_API, key))
			return ""

		return value

	def storeList(self, dataList):
		"""store list of artefacts"""
		raise NotImplementedError

	def retrieveList(self, key):
		"""retrieve list of artefacts"""
		raise NotImplementedError

