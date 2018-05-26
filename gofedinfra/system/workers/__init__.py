import os
import sys
from collections import namedtuple

from ansible.parsing.dataloader import DataLoader
try:
    from ansible.vars import VariableManager
    old_ansible = True
except ImportError:
    from ansible.vars.manager import VariableManager
    old_ansible = False

if old_ansible:
    from ansible.inventory import Inventory
else:
    from ansible.inventory.manager import InventoryManager
    from ansible.playbook.play import Play

from ansible.executor.playbook_executor import PlaybookExecutor

from gofedlib.utils import getScriptDir
import logging

#
# Currently only Ansible based workers.
# Later, k8s job based workers will be supported as well.
#
# It is assumed the ansible/k8s job itself does not return any data.
# Only its success/fail state. Any data needs to be requested separately.

class WorkerException(Exception):
    pass

class Worker(object):

    def __init__(self, name):
        self._playbook = name
        self._playbook_dir = getScriptDir(file = __file__) + "/../../../ansible/playbooks"

    def setPayload(self, data):
        # TOOD(jchaloup): validate the vars in the data are accepted by the playbook
        self._data = data
        return self

    def do(self):
        if old_ansible:
            self._variable_manager = VariableManager()
            self._loader = DataLoader()
            self._inventory = Inventory(
                loader=self._loader,
                variable_manager=self._variable_manager,
            )
        else:
            self._loader = DataLoader()
            self._inventory = InventoryManager(
                loader=self._loader,
            )
            self._variable_manager = VariableManager(
                loader=self._loader,
                inventory=self._inventory,
            )

        options = [
            'listtags',
            'listtasks',
            'listhosts',
            'syntax',
            'connection',
            'module_path',
            'forks',
            'remote_user',
            'private_key_file',
            'ssh_common_args',
            'ssh_extra_args',
            'sftp_extra_args',
            'scp_extra_args',
            'become',
            'become_method',
            'become_user',
            'verbosity',
            'check'
        ]

        if not old_ansible:
            options.append('diff')

        Options = namedtuple(
            'Options', options
        )

        if old_ansible:
            self._options = Options(
                listtags=False,
                listtasks=False,
                listhosts=False,
                syntax=False,
                connection='local',
                module_path=None,
                forks=100,
                remote_user='gofed',
                private_key_file=None,
                ssh_common_args=None,
                ssh_extra_args=None,
                sftp_extra_args=None,
                scp_extra_args=None,
                become=False,
                become_method=None,
                become_user='root',
                verbosity=None,
                check=False
            )
        else:
            self._options = Options(
                listtags=False,
                listtasks=False,
                listhosts=False,
                syntax=False,
                connection='local',
                module_path=None,
                forks=100,
                remote_user='gofed',
                private_key_file=None,
                ssh_common_args=None,
                ssh_extra_args=None,
                sftp_extra_args=None,
                scp_extra_args=None,
                become=False,
                become_method=None,
                become_user='root',
                verbosity=None,
                check=False,
                diff=False
            )

        extra_vars = {}
        for key in self._data:
            extra_vars[key] = self._data[key]

        self._variable_manager.extra_vars = extra_vars

        playbook_path = self._playbook_dir + "/" + self._playbook + ".yml"

        if not os.path.exists(playbook_path):
            raise ValueError("The playbook {} does not exist".format(playbook_path))

        stdout = sys.stdout
        # Hacky but working
        if logging.getLogger().level != logging.WARNING:
            sys.stdout = open(os.devnull, 'w')

        pe = PlaybookExecutor(playbooks=[playbook_path], inventory=self._inventory, variable_manager=self._variable_manager, loader=self._loader, options=self._options, passwords={})
        if pe.run() != 0:
            raise WorkerException("Ansible playbook {} failed".format(self._playbook))

        if logging.getLogger().level != logging.WARNING:
            sys.stdout.close()
            sys.stdout = stdout

        return self
