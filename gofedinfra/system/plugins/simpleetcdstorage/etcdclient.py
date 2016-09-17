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
		# TODO(jchaloup): check if etcd is actually running
		logging.info("etcdctl set \"%s\"" % key)
		p = Popen("etcdctl set \"%s\"" % key, stderr=PIPE, stdout=PIPE, stdin=PIPE, shell=True)
		try:
			p.stdin.write(value)
		except IOError as e:
			logging.error("Unable to set %s: %s" % (key, e))
			return False

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
