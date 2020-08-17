import pytest
from functools import wraps

def run_on_all_asics(f):
    pdb.set_trace()
    @wraps(f)
    def wrapper(duthost, localhost, creds, *args, **kwargs):
        asics =  duthost.num_asics()
        if asics == 1:
            config_facts  = duthost.config_facts(host=duthost.hostname, source="persistent", filename="/etc/sonic/config_db.json", num_asic=asics)['ansible_facts']
            f(duthost, localhost, creds, config_facts, *args, **kwargs)
        else:
            for asic_inst in range(asics):
                filename = "/etc/sonic/config_db" + str(asic_inst) + ".json"
                config_facts  = duthost.config_facts(host=duthost.hostname, source="persistent", filename=filename, num_asic=asics)['ansible_facts']
                f(duthost, localhost, creds, config_facts, *args, **kwargs)
    return wrapper

@run_on_all_asics
@pytest.mark.bsl
def test_snmp_interfaces(duthost, localhost, creds, config_facts):
    """compare the bgp facts between observed states and target state"""

    hostip = duthost.host.options['inventory_manager'].get_host(duthost.hostname).vars['ansible_host']

    asics =  duthost.num_asics()

    snmp_facts = localhost.snmp_facts(host=hostip, version="v2c", community=creds["snmp_rocommunity"])['ansible_facts']

    snmp_ifnames = [ v['name'] for k, v in snmp_facts['snmp_interfaces'].items() ]
    print snmp_ifnames
    for _, alias in config_facts['port_name_to_alias_map'].items():
        assert alias in snmp_ifnames
    for po_name in config_facts.get('PORTCHANNEL', {}):
        assert po_name in snmp_ifnames

@pytest.mark.bsl
def test_mgmt_interfaces(duthost, localhost, creds):
    pdb.set_trace()
    hostip = duthost.host.options['inventory_manager'].get_host(duthost.hostname).vars['ansible_host']
    asics =  duthost.num_asics()
    snmp_facts = localhost.snmp_facts(host=hostip, version="v2c", community=creds["snmp_rocommunity"])['ansible_facts']
    config_facts  = duthost.config_facts(host=duthost.hostname, source="persistent", num_asic=asics)['ansible_facts']
    snmp_ifnames = [ v['name'] for k, v in snmp_facts['snmp_interfaces'].items() ]
    for _, alias in config_facts['mgmt_port_name_to_alias_map'].items():
        assert alias in snmp_ifnames, "Mgmt interface not in SNMP output"
