from gofed_lib.packagemanager import PackageManager
import koji
import json

from system.acts.scandistributionbuild.act import ScanDistributionBuildAct

if __name__ == "__main__":
	server = "http://koji.fedoraproject.org/kojihub/"
	session = koji.ClientSession(server)

	act = ScanDistributionBuildAct()

	# get a list of all packages
	packages = PackageManager().getPackages()

	# fetch names of the latest builds for rawhide (ping DH if I can use some of it)
	for pkg in packages:
		data = session.getLatestRPMS("rawhide", package="golang-gopkg-check")
		build = "%s-%s-%s" % (data[1][0]["package_name"], data[1][0]["version"], data[1][0]["release"])
		rpms = []
		for rpm in data[0]:
			if rpm["arch"] != "noarch":
				continue

			if not rpm["name"].endswith("devel"): # and not rpm["name"].endswith("unit-test"):
				continue

			rpm_obj = {
				"name": "%s-%s-%s.%s.rpm" % (rpm["name"], rpm["version"], rpm["release"], rpm["arch"]),
				# TODO(jchaloup): autodetect directories with deps
				# what is a standard way for:
				# - Godeps
				# - vendor
				# - experimental
				# - other known dirs?
				"skipped_directories": ["Godeps"]
			}

			rpms.append(rpm_obj)

		data = {
			"product": "Fedora",
			"distribution": "rawhide",
			"build": {
				"name": build,
				"rpms": rpms
			}
		}

		print data

		print "Setting:"
		print act.setData(data)
	
		print "Executing:"
		print act.execute()
	
		print "Getting:"
		#act.getData()
		print json.dumps(act.getData())
		break
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


