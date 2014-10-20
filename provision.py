#!/usr/bin/python3
import subprocess
import json
import time
import urllib.request
import tempfile

def install_salt():
    '''Install Salt on a local machine'''
    resp = urllib.request.urlopen('https://bootstrap.saltstack.com')
    assert resp.status == 200
    with tempfile.NamedTemporaryFile(mode='w+b') as f:
        f.write(resp.read())
        f.flush()
        subprocess.check_call(
            'sh {} -M -i local -A 127.0.0.1'.format(
                f.name
            ).split()
        )
    print(0)


def setup_salt():
    time.sleep(1)
    subprocess.check_call('sudo salt-key -Ay'.split())


def test_salt():
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


def highstate_salt():
    subprocess.check_call('sudo salt-call state.highstate'.split())


def main():
    #install_salt()
    #setup_salt()
    test_salt()
    highstate_salt()


if __name__ == '__main__':
    main()
