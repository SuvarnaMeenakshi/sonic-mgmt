import pytest
@pytest.mark.bsl

def test_snmp_interfaces(duthost, localhost, creds):
    """compare the bgp facts between observed states and target state"""

    hostip = duthost.host.options['inventory_manager'].get_host(duthost.hostname).vars['ansible_host']

    asics =  duthost.num_asics()

    snmp_facts = localhost.snmp_facts(host=hostip, version="v2c", community=creds["snmp_rocommunity"])['ansible_facts']

    snmp_ifnames = [ v['name'] for k, v in snmp_facts['snmp_interfaces'].items() ]
    print snmp_ifnames
    config_facts = duthost.get_config_facts("persistent")

    for _, alias in config_facts['global']['mgmt_port_name_to_alias_map'].items():
        assert alias in snmp_ifnames, "Mgmt interface not in SNMP output"

    for asic_inst in range(asics):
        for _, alias in config_facts[str(asic_inst)]['port_name_to_alias_map'].items():
            assert alias in snmp_ifnames, "Interface not in SNMP output"
        for po_name in config_facts[str(asic_inst)].get('PORTCHANNEL', {}):
            assert po_name in snmp_ifnames, "PortChannel not in SNMP output"
