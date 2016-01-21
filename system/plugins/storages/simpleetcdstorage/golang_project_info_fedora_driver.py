from system.plugins.storages.metaartefactdriver import MetaArtefactDriver
from system.helpers.artefactkeygenerator.golang_project_info_fedora import GolangProjectInfoFedoraKeyGenerator
from etcdclient import EtcdClient
import json
import logging

class GolangProjectInfoFedoraDriver(MetaArtefactDriver):

	def store(self, data):
		"""store artefact"""
		# generate key
		key = GolangProjectInfoFedoraKeyGenerator().generate(data)
		if key == "":
			logging.error("Unable to store golang-project-fedora-info artefact: key not generated")
			return False

		# store the data into etcd
		if EtcdClient().set(key, json.dumps(data)):
			logging.error("Unable to store golang-project-fedora-info artefact with '%s' key" % key)
			return False

		return True

	def retrieve(self, key_data):
		"""retrieve artefact"""
		key = GolangProjectInfoFedoraKeyGenerator().generate(key_data)
		if key == "":
			logging.error("Unable to store golang-project-fedora-info artefact: key not generated")
			return False

		# get the data from etcd
		ok, value = EtcdClient().get(key)

		if not ok:
			logging.error("Unable to retrieve golang-project-fedora-info artefact with '%s' key" % key)
			return ""

		return value

	def storeList(self, dataList):
		"""store list of artefacts"""
		raise NotImplementedError

	def retrieveList(self, key):
		"""retrieve list of artefacts"""
		raise NotImplementedError

