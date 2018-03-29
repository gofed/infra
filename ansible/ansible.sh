#!/bin/sh

CUR_DIR=/home/jchaloup/Projects/gofed/infra/ansible/../../gofed/hack

export PYTHONPATH=${CUR_DIR}/../third_party/gofedlib:${CUR_DIR}/../../infra:${CUR_DIR}/../..

ansible-playbook "$@"
#./run.py
