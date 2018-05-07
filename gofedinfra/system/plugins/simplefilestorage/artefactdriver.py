import logging
logger = logging.getLogger("simple_file_storage")

from infra.system.core.meta.metaartefactdriver import MetaArtefactDriver
from infra.system.artefacts import artefacts
from infra.system.helpers.artefactkeygenerator.keygenerator import KeyGeneratorFactory
import os
import json
from distutils.dir_util import mkpath
from distutils.errors import DistutilsFileError

class ArtefactDriver(object):

	def __init__(self, working_directory, artefact = artefacts.ARTEFACT_NO_ARTEFACT):
		self.working_directory = working_directory
		self.artefact = artefact

	def _generateKey(self, data):
		generator = KeyGeneratorFactory().build(self.artefact)
		if generator == None:
			raise KeyError("Unable to process %s artefact: key generator not found" % self.artefact)

		key = generator.generate(data)
		if key == []:
			raise KeyError("Unable to process %s artefact: key not generated" % self.artefact)

		return reduce(lambda a,b: os.path.join(a, b), key)

	def retrieve(self, key_data):
		"""retrieve artefact"""
		key = self._generateKey(key_data)

		# file exists?
		data_path = os.path.join(self.working_directory, key)
		data_file = os.path.join(data_path, "data.json")

		try:
			# TODO(jchaloup): lock the file and unlock after reading
			with open(data_file, "r") as f:
				return json.load(f)
		except IOError as e:
			logger.info("Unable to retrieve {} artefact with '{}' key under {}".format(self.artefact, key, self.working_directory))
			raise KeyError("Unable to retrieve {} artefact with '{}' key under {}".format(self.artefact, key, self.working_directory))

		return {}

	def store(self, data):
		"""store artefact"""
		key = self._generateKey(data)

		data_path = os.path.join(self.working_directory, key)

		# mkdir -p data_path
		# http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
		try:
			mkpath(data_path)
		except DistutilsFileError as e:
			logging.error(e)
			raise IOError(e)
		# it is okay to ignore IOError exception
		#except IOError as e:

		# TODO(jchaloup): check if the file exists, if so, lock it?
		with file(os.path.join(data_path, "data.json"), "w") as f:
			json.dump(data, f)
		# it is okay to ignore IOError exception
		return os.path.join(data_path, "data.json")
