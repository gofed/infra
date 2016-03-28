class Snapshot(object):

	def __init__(self):
		self.packages = {}

	def addPackage(self, package, commit):
		self.packages[package] = commit

	def Godeps(self):
		"""Return the snapshot in Godeps.json form

		"""
		for package in self.packages:
			print {
				"ImportPath": str(package),
				"Rev": str(self.packages[package])
			}
