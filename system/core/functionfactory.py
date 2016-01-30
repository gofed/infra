from basicfunction import BasicFunction
from system.helpers.utils import getScriptDir
import os
import json
import logging
import imp
import importlib

class FunctionNotFoundError(RuntimeError):
   def __init__(self, err):
      self.err = err

class FunctionFactory:
	"""
	Factory baking functions

	https://github.com/gofed/infra/issues/10
	"""

	def __init__(self):
		self.recipes = {}
		self._detectPlugins()

	def _detectPlugins(self):
		plugins_dir = "%s/../plugins" % getScriptDir(__file__)
		# TODO(jchaloup): check if the directory exists
		for dirName, subdirList, fileList in os.walk(plugins_dir):
			register_file = "%s/register.json" % (dirName)
			if not os.path.exists(register_file):
				continue

			reg_obj = {}
			with open(register_file, "r") as f:
				reg_obj = json.load(f)
				# TODO(jchaloup): in future add support for more ID->class pairs in register.json
				if "id" not in reg_obj or "class" not in reg_obj or "file" not in reg_obj:
					logging.warning("plugin not loaded, invalid register.json: %s" % reg_obj)
					continue

				self.recipes[reg_obj["id"]] = {
					"class": reg_obj["class"],
					"import": "%s.%s" % (os.path.basename(dirName), reg_obj["file"].split(".")[-2])
				}

	def bake(self, function_ID):
		if function_ID not in self.recipes:
			# throw exception 'function ID not found'
			raise FunctionNotFoundError("function %s not found" % function_ID)

		# TODO(jchaloup): catch exception, does the class exists, ... other checks
		module = importlib.import_module("system.plugins.%s" % self.recipes[function_ID]["import"])
		obj = getattr(module, "GoSymbolExtractor")()
		# TODO(jchaloup): add support for proxy and other kind functions
		return BasicFunction(obj)
		
