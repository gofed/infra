from system.helpers.utils import runCommand
import logging
import tempfile

MAXIMUM_VALUE_LEN = 1000

class EtcdClient:
	"""
	Client for etcd key-value database.

	TODO(jchaloup): rewritte the class to use real etcd client.
	This class forwards all request to 'etcdctl' command in shell.
	"""

	def set(self, key, value):
		# key and values are string => escape quotes
		escaped_key = key.replace('"', '\\"')
		escaped_value = value.replace('"', '\\"')

		# if the value is too long, save it into a file
		if len(escaped_value) > MAXIMUM_VALUE_LEN:
			f = tempfile.NamedTemporaryFile(delete=False)
			with open(f.name, 'w') as s:
				s.write(value)
			cmd = "etcdctl set \"%s\" < %s" % (escaped_key, f.name)
			so, se, rc = runCommand(cmd)
			if rc != 0:
				logging.error(se)
				return False
			f.close()
		else:
			cmd = "etcdctl set \"%s\" \"%s\"" % (escaped_key, escaped_value)
			so, se, rc = runCommand(cmd)
			if rc != 0:
				logging.error(se)
				return False
		return True

	def get(self, key):
		# key and values are string => escape quotes
		escaped_key = key.replace('"', '\\"')

		cmd = "etcdctl get \"%s\"" % escaped_key
		so, se, rc = runCommand(cmd)
		if rc != 0:
			logging.error(se)
			return False, ""

		return True, so.split("\n")[0]
