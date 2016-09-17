from gofedlib.packagemanager import PackageManager
import json
import traceback
import sys

from gofedinfra.system.acts.scandistributionbuild.act import ScanDistributionBuildAct
from gofedlib.kojiclient import FakeKojiClient, KojiClient
from gofedlib.helpers import Rpm

import logging
#logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":

	client = KojiClient()

	act = ScanDistributionBuildAct()

	# get a list of all packages
	packages = PackageManager().getPackages()

	# fetch names of the latest builds for rawhide (ping DH if I can use some of it)
	for pkg in packages:
		try:
			data = client.getLatestRPMS("rawhide", pkg)
		except ValueError as e:
			logging.error(e)
			continue
		except KeyError as e:
			logging.error(e)
			continue

		rpms = []
		for rpm in data["rpms"]:
			rpm_name = Rpm(data["name"], rpm["name"]).name()
			if not rpm_name.endswith("devel"): # and not rpm["name"].endswith("unit-test"):
				continue

			# Some devel subpackage may still be arch specific
			#if rpm["arch"] != "noarch":
			#	continue

			rpm_obj = {
				"name": rpm["name"]
			}

			rpms.append(rpm_obj)

		if rpms == []:
			print "List of rpms empty\n"
			continue

		data = {
			"product": "Fedora",
			"distribution": "rawhide",
			"build": {
				"name": data["name"],
				"rpms": rpms
			}
		}

		print data

		try:
			#print "Setting:"
			if not act.setData(data):
				print "setData Error: %s\n" % pkg
	
			#print "Executing:"
			if not act.execute():
				print "execute Error: %s\n" % pkg
		except:
			exc_info = sys.exc_info()
			traceback.print_exception(*exc_info)
			del exc_info

		print ""
	
		#print "Getting:"
		#act.getData()
		#print json.dumps(act.getData())
		#break
# for each build get a list of devel subpackages (make asumption: pkg-devel.noarch.rpm)
#rpms = session.getLatestRPMS("rawhide", package="etcd")

# run acts on individual rpms (make the act self-standing binary?)

# source codes of each rpm are installed/extracted under ./usr/share/gocode/src/IPPREFIX/...
# based on the path I can detect all ip prefix provided by a devel rpm. So the prefix can be detected automatically

# store all artefacts to db (could be part of the act input)

# QUESTIONS
# - make every act a self-standing binary?
#
#
#
#


