class PureFunction:
	"""
	Wrapper for pure functions.
	There will be single wrapper for all pure functions.
	It is return from a factory to provide uniform interface.

	https://github.com/gofed/infra/issues/9
	"""

	def __init__(self, fnc):
		"""Set callable object"""
		self.fnc = fnc

	def call(self, data):
		"""Call a function with the given data"""
		return self.fnc(data)

def a(d):
	print(d)

if __name__ == "__main__":
	pf = PureFunction(a)
	pf.call("Ahoj")
