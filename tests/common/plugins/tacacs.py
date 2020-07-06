import pytest
import crypt

def start_tacacs(ptfhost, duthost, creds, tacacs_server_ip):
    """setup tacacs client and server"""

    # disable tacacs server
    ptfhost.service(name="tacacs_plus", state="stopped")

    # configure tacacs client
    duthost.shell("sudo config tacacs passkey %s" % creds['tacacs_passkey'])

    # get default tacacs servers
    config_facts  = duthost.config_facts(host=duthost.hostname, source="running")['ansible_facts']
    for tacacs_server in config_facts.get('TACPLUS_SERVER', {}):
        duthost.shell("sudo config tacacs delete %s" % tacacs_server)
    duthost.shell("sudo config tacacs add %s" % tacacs_server_ip)
    duthost.shell("sudo config tacacs authtype login")

    # enable tacacs+
    duthost.shell("sudo config aaa authentication login tacacs+")

    # configure tacacs server
    extra_vars = {'tacacs_passkey': creds['tacacs_passkey'],
                  'tacacs_rw_user': creds['tacacs_rw_user'],
                  'tacacs_rw_user_passwd': crypt.crypt(creds['tacacs_rw_user_passwd'], 'abc'),
                  'tacacs_ro_user': creds['tacacs_ro_user'],
                  'tacacs_ro_user_passwd': crypt.crypt(creds['tacacs_ro_user_passwd'], 'abc')}

    ptfhost.host.options['variable_manager'].extra_vars.update(extra_vars)
    ptfhost.template(src="tacacs/tac_plus.conf.j2", dest="/etc/tacacs+/tac_plus.conf")

    # start tacacs server
    ptfhost.service(name="tacacs_plus", state="started")


def cleanup_tacacs(ptfhost, duthost, tacacs_server_ip):
    # stop tacacs server
    ptfhost.service(name="tacacs_plus", state="stopped")

    # reset tacacs client configuration
    duthost.shell("sudo config tacacs delete %s" % tacacs_server_ip)
    duthost.shell("sudo config tacacs default passkey")
    duthost.shell("sudo config aaa authentication login default")
    duthost.shell("sudo config aaa authentication failthrough default")

@pytest.fixture(scope="module")
def setup_tacacs(ptfhost, duthost, creds):
    tacacs_server_ip = ptfhost.host.options['inventory_manager'].get_host(ptfhost.hostname).vars['ansible_host']
    start_tacacs(ptfhost, duthost, creds, tacacs_server_ip)

    yield

    cleanup_tacacs(ptfhost, duthost, tacacs_server_ip)


@pytest.fixture(scope="module")
def setup_tacacs_v6(ptfhost, duthost, creds):
    tacacs_server_ip = ptfhost.host.options['inventory_manager'].get_host(ptfhost.hostname).vars['ansible_hostv6']
    start_tacacs(ptfhost, duthost, creds, tacacs_server_ip)

    yield

    cleanup_tacacs(ptfhost, duthost, tacacs_server_ip)
