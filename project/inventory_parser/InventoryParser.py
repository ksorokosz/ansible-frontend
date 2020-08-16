# Inventory parser
#

from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from operator import attrgetter

class UnknownApplication(Exception):
    pass

INTERNAL_VARS = frozenset(['ansible_diff_mode',
                           'ansible_config_file',
                           'ansible_facts',
                           'ansible_forks',
                           'ansible_inventory_sources',
                           'ansible_limit',
                           'ansible_playbook_python',
                           'ansible_run_tags',
                           'ansible_skip_tags',
                           'ansible_verbosity',
                           'ansible_version',
                           'inventory_dir',
                           'inventory_file',
                           'inventory_hostname',
                           'inventory_hostname_short',
                           'groups',
                           'group_names',
                           'omit',
                           'playbook_dir', ])

class InventoryParser:

    def __init__(self, vault_pass = None):

        self.data_loader = DataLoader()
        self.vault_pass = vault_pass
        if self.vault_pass:
            loader.set_vault_password(self.vault_pass)

    @staticmethod
    def _remove_empty(dump):
        # remove empty keys
        for x in ('hosts', 'vars', 'children'):
            if x in dump and not dump[x]:
                del dump[x]

    @staticmethod
    def _remove_internal(dump):

        for internal in INTERNAL_VARS:
            if internal in dump:
                del dump[internal]

        return dump

    def json_inventory(self, top):

        seen = set()

        def format_group(group):
            results = {}
            results[group.name] = {}
            if group.name != 'all':
                results[group.name]['hosts'] = [h.name for h in sorted(group.hosts, key=attrgetter('name'))]
            results[group.name]['children'] = []
            for subgroup in sorted(group.child_groups, key=attrgetter('name')):
                results[group.name]['children'].append(subgroup.name)
                if subgroup.name not in seen:
                    results.update(format_group(subgroup))
                    seen.add(subgroup.name)

            self._remove_empty(results[group.name])
            if not results[group.name]:
                del results[group.name]

            return results

        results = format_group(top)

        # populate meta
        results['_meta'] = {'hostvars': {}}
        hosts = top.get_hosts()
        for host in hosts:
            hvars = self._remove_internal(self.variable_manager.get_vars(host=host, include_hostvars=False))
            if hvars:
                results['_meta']['hostvars'][host.name] = hvars

        return results

    def parse(self, inventory_file, application):

        self.inventory = InventoryManager(loader = self.data_loader, sources=inventory_file)
        self.variable_manager = VariableManager(loader = self.data_loader, inventory = self.inventory)
        top = self.inventory.groups.get(application)
        if not top:
            raise UnknownApplication("Unknown application: {}. Should be one of existing inventory group".format(application))
        return self.json_inventory(top)
