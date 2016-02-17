from system.helpers.utils import getScriptDir

import os
import json
import logging
import imp
import importlib

class Factory:
	"""
	"""

	def __init__(self, registration_directory):
		self._registration_directory = registration_directory

		self.recipes = {}
		self._detectPlugins()

	def _checkRegistration(self, reg_obj):
		if "id" not in reg_obj or "class" not in reg_obj or "file" not in reg_obj:
			return False
		return True

	def _detectPlugins(self):
		# TODO(jchaloup): check if the registration directory exists
		plugins_dir = "%s/../../plugins" % getScriptDir(__file__)
		# TODO(jchaloup): check if the directory exists
		for dirName, subdirList, fileList in os.walk(self._registration_directory):
			register_file = "%s/register.json" % (dirName)
			if not os.path.exists(register_file):
				continue

			reg_obj = {}
			with open(register_file, "r") as f:
				reg_obj = json.load(f)

				if type(reg_obj) != type([]):
					reg_obj = [reg_obj]

				for reg in reg_obj:
					if not self._checkRegistration(reg):
						logging.warning("Unable to register %s, invalid register.json: %s" % (reg["id"], reg))
						continue

					self.recipes[reg["id"]] = {
						"class": reg["class"],
						"import": "%s.%s" % (os.path.basename(dirName), reg["file"].split(".")[-2])
					}

	def bake(self, item_ID):
		if item_ID not in self.recipes:
			raise ValueError("Unable to find '%s' ID" % item_ID)

		# TODO(jchaloup): catch exception, does the class exists, ... other checks
		module = importlib.import_module("system.plugins.%s" % self.recipes[item_ID]["import"])
		if not hasattr(module, self.recipes[item_ID]["class"]):
			raise ValueError("Unable to bake '%s': class '%s' not found" % (item_ID, self.recipes[item_ID]["class"]))

		return getattr(module, self.recipes[item_ID]["class"])()

