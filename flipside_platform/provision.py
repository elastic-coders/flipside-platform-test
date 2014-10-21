#!/usr/bin/python3
'''Install and configure salt on the local machine.'''
import subprocess
import json
import time
import urllib.request
import tempfile


def install_salt(standalone):
    '''Install Salt on the local machine'''
    resp = urllib.request.urlopen('https://bootstrap.saltstack.com')
    assert resp.status == 200
    with tempfile.NamedTemporaryFile(mode='w+b') as f:
        f.write(resp.read())
        f.flush()
        subprocess.check_call(
            'sh {script} {opts}'.format(
                script=f.name,
                opts='-M -N' if standalone else '-i local -A 127.0.0.1'
            ).split()
        )


def setup_salt(standalone):
    if standalone:
        with open('/etc/salt/minion', 'w+') as f:
            f.write('file_client:\n  local\n')
    else:
        time.sleep(1)
        subprocess.check_call('sudo salt-key -Ay'.split())


def test_salt(standalone):
    if standalone:
        return
    for i in range(2):
        ping = json.loads(
            subprocess.check_output(
                'sudo salt * test.ping --out json --static'.split()
            ).decode()
        )
    if ping.get('local'):
        print('OK')
    else:
        raise SystemExit('ERROR')


def highstate_salt(standalone):
    subprocess.check_call('sudo salt-call state.highstate'.split())


def main(standalone=True, highstate=True):
    install_salt(standalone)
    setup_salt(standalone)
    test_salt(standalone)
    if highstate:
        highstate_salt(standalone)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-standalone', action='store_true')
    parser.add_argument('--no-highstate', action='store_true')
    args = parser.parse_args()
    main(standalone=not args.no_standalone, highstate=not args.no_highstate)
