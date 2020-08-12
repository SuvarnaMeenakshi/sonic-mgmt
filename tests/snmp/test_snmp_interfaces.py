import pytest

@pytest.mark.bsl
def test_snmp_interfaces(duthost, localhost, creds):
    """compare the bgp facts between observed states and target state"""

    hostip = duthost.host.options['inventory_manager'].get_host(duthost.hostname).vars['ansible_host']

    asics =  duthost.num_asics()

    snmp_facts = localhost.snmp_facts(host=hostip, version="v2c", community=creds["snmp_rocommunity"])['ansible_facts']

    snmp_ifnames = [ v['name'] for k, v in snmp_facts['snmp_interfaces'].items() ]
    print snmp_ifnames

    config_facts  = duthost.config_facts(host=duthost.hostname, source="persistent", num_asic=asics)['ansible_facts']
    if (asics > 1):
        # Verify management port in snmp interface list
        for _, alias in config_facts[u'global']['mgmt_port_name_to_alias_map'].items():
            assert alias in snmp_ifnames, "Mgmt interface not in SNMP output"
        for asic_inst in range(asics):
            for _, alias in config_facts[str(asic_inst).encode()]['port_name_to_alias_map'].items():
                assert alias in snmp_ifnames, "Interface not in SNMP output"
            for po_name in config_facts[str(asic_inst).encode()].get('PORTCHANNEL', {}):
                assert po_name in snmp_ifnames, "PortChannel not in SNMP output"
    else:
        # Verify management port in snmp interface list
        for _, alias in config_facts['mgmt_port_name_to_alias_map'].items():
            assert alias in snmp_ifnames, "Mgmt interface not in SNMP output"
        for _, alias in config_facts['port_name_to_alias_map'].items():
            assert alias in snmp_ifnames
        for po_name in config_facts.get('PORTCHANNEL', {}):
            assert po_name in snmp_ifnames
