import sys

if __name__ == "gofed_infra":
	sys.modules['infra'] = sys.modules[__name__]
