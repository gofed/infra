from infra.system.helpers.utils import runCommand
import logging
import tempfile
from subprocess import PIPE, Popen

class EtcdClient:
	"""
	Client for etcd key-value database.

	TODO(jchaloup): rewritte the class to use real etcd client.
	This class forwards all request to 'etcdctl' command in shell.
	"""

	def set(self, key, value):
		# values are string => escape quotes
		escaped_value = value.replace('"', '\\"').replace('\\\\"', '\\\\\\"')

		p = Popen("etcdctl set \"%s\"", stderr=PIPE, stdout=PIPE, stdin=PIPE, shell=True)
		p.stdin.write(escaped_value)
		so, se = p.communicate()
		p.stdin.close()
		rc = p.returncode
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
