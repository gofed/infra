class ClassHelper:

	def __init__(self, key_spec):
		self.key_spec = key_spec
		self._generate()

	def _generate(self):
		self._class_name = "".join(map(lambda i: i.capitalize(), self.key_spec["id"].split("-")))
		self._class_keys = '["' + '", "'.join(self.key_spec["keys"]) + '"]'
		self._class_filename_ext = "%s.py" % self.key_spec["id"].replace("-", "")
		self._class_filename = self.key_spec["id"].replace("-", "")

	def class_name(self):
		return self._class_name

	def class_keys(self):
		return self._class_keys

	def class_filename(self):
		return self._class_filename

	def class_filename_ext(self):
		return self._class_filename_ext

