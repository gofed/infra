from basicfunction import BasicFunction
from storagefunction import StorageFunction
from system.helpers.utils import getScriptDir
from system.core.meta.metaprocessor import MetaProcessor
from system.core.meta.metastoragereader import MetaStorageReader
from system.core.meta.metastoragewriter import MetaStorageWriter
from types import FunctionNotFoundError

import os
import json
import logging
import imp
import importlib

class FunctionFactory:
	"""
	Factory baking functions

	https://github.com/gofed/infra/issues/10
	"""

	def __init__(self):
		self.recipes = {}
		self._detectPlugins()

	def _checkRegistration(self, reg_obj):
		if "id" not in reg_obj or "class" not in reg_obj or "file" not in reg_obj:
			return False
		return True

	def _detectPlugins(self):
		# TODO(jchaloup): put plugins_dir into config file
		# TODO(jchaloup): check if the plugin directory exists
		plugins_dir = "%s/../../plugins" % getScriptDir(__file__)
		# TODO(jchaloup): check if the directory exists
		for dirName, subdirList, fileList in os.walk(plugins_dir):
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
						logging.warning("plugin %s not loaded, invalid register.json: %s" % (reg["id"], reg))
						continue

					self.recipes[reg["id"]] = {
						"class": reg["class"],
						"import": "%s.%s" % (os.path.basename(dirName), reg["file"].split(".")[-2])
					}

	def bake(self, function_ID):
		if function_ID not in self.recipes:
			raise FunctionNotFoundError("function %s not found" % function_ID)

		# TODO(jchaloup): catch exception, does the class exists, ... other checks
		module = importlib.import_module("system.plugins.%s" % self.recipes[function_ID]["import"])
		if not hasattr(module, self.recipes[function_ID]["class"]):
			raise FunctionNotFoundError("function %s not bakeable: class %s not found" % (function_ID, self.recipes[function_ID]["class"]))

		obj = getattr(module, self.recipes[function_ID]["class"])()
		if isinstance(obj, MetaProcessor):
			return BasicFunction(obj)
		elif isinstance(obj, MetaStorageReader) or isinstance(obj, MetaStorageWriter):
			return StorageFunction(obj)

		raise FunctionNotFoundError("function %s not bakeable: function kind not supported" % function_ID)
