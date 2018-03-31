.PHONY: test

test:
	cd ansible && PYTHONPATH=$$(pwd)/../third_party/gofedlib:$$(pwd)/../../infra:$$(pwd)/../.. ansible-playbook test.yml
