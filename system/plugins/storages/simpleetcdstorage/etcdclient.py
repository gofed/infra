from system.helpers.utils import runCommand
import logging

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

		cmd = "etcdctl set \"%s\" \"%s\"" % (escaped_key, escaped_value)
		so, se, rc = runCommand(cmd)
		if rc != 0:
			logging.error(se)
			return False
		else:
			logging.info(so)

	def get(self, key):
		# key and values are string => escape quotes
		escaped_key = key.replace('"', '\\"')

		cmd = "etcdctl get \"%s\"" % escaped_key
		so, se, rc = runCommand(cmd)
		if rc != 0:
			logging.error(se)
			return False, ""

		return True, so.split("\n")[0]
