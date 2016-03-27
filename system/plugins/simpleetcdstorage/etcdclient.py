from infra.system.helpers.utils import runCommand
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
		# values are string => escape quotes
		escaped_value = value.replace('"', '\\"').replace('\\\\"', '\\\\\\"')
		# if the value is too long, save it into a file
		if len(escaped_value) > MAXIMUM_VALUE_LEN:
			f = tempfile.NamedTemporaryFile(delete=True)
			with open(f.name, 'w') as s:
				s.write(value)
			cmd = "etcdctl set \"%s\" < %s" % (key, f.name)
			so, se, rc = runCommand(cmd)
			if rc != 0:
				logging.error("%s, len: %s" % (se, len(escaped_value)))
				return False
			f.close()
		else:
			cmd = "etcdctl set \"%s\" \"%s\"" % (key, escaped_value)
			so, se, rc = runCommand(cmd)
			if rc != 0:
				logging.error(se)
				return False
		return True

	def get(self, key):

		cmd = "etcdctl get \"%s\"" % key
		logging.info(cmd)
		so, se, rc = runCommand(cmd)
		if rc != 0:
			logging.info(se)
			return False, ""

		value = so.split("\n")[0]
		return True, value
