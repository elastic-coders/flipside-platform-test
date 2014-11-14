#!/usr/bin/python3
'''Install and configure salt on the local machine.'''
import subprocess
import json
import time
import urllib.request
import tempfile
import os


def install_salt(standalone, version='stable'):
    '''Install Salt on the local machine'''
    resp = urllib.request.urlopen('https://bootstrap.saltstack.com')
    assert resp.status == 200
    with tempfile.NamedTemporaryFile(mode='w+b') as f:
        f.write(resp.read())
        f.flush()
        subprocess.check_call(
            'sh {script} {opts} -n -p python-pip -p python-dev -p libtiff4-dev -p libjpeg8-dev -p zlib1g-dev -p libfreetype6-dev -p liblcms2-dev -p libwebp-dev -p libffi-dev -p cmake {version}'.format(
                script=f.name,
                opts='-M -N -X' if standalone else '-i local -A 127.0.0.1',
                version=version
            ).split()
        )
        if not subprocess.check_output('pip show pygit2'.split()):
            subprocess.check_call(['bash', '-c', 'wget https://github.com/libgit2/libgit2/archive/v0.21.2.tar.gz && tar xzf v0.21.2.tar.gz && cd libgit2-0.21.2/ && cmake . && make && sudo make install'], cwd='/tmp')
            subprocess.check_call('pip install pygit2==0.21.4'.split())
        else:
            print('pygit2 already installed')


def setup_salt(standalone):
    # XXX Maybe we could simply use salt to... bootstrap salt
    if not os.path.exists('/etc/salt/master.d'):
        os.mkdir('/etc/salt/master.d')
    if not os.path.exists('/etc/salt/minion.d'):
        os.mkdir('/etc/salt/minion.d')
    gitfs_config = 'fileserver_backend:\n  - roots\n  - git\n\ngitfs_remotes:\n  - https://github.com/saltstack-formulas/nginx-formula.git\n'
    if standalone:
        # XXX use minion.d instead
        with open('/etc/salt/minion', 'w+') as f:
            f.write('file_client:\n  local\n')
        with open('/etc/salt/minion.d/flipside_gitfs.conf', 'w+') as f:
            f.write(gitfs_config)
    else:
        with open('/etc/salt/master.d/flipside_gitfs.conf', 'w+') as f:
            f.write(gitfs_config)
        subprocess.check_call('sudo service salt-master restart')
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


def main(standalone=True, highstate=True, salt_version=None):
    install_salt(standalone, salt_version)
    setup_salt(standalone)
    test_salt(standalone)
    if highstate:
        highstate_salt(standalone)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-standalone', action='store_true')
    parser.add_argument('--no-highstate', action='store_true')
    parser.add_argument('--salt-version', default='stable')
    args = parser.parse_args()
    main(standalone=not args.no_standalone, highstate=not args.no_highstate,
         salt_version=args.salt_version)
