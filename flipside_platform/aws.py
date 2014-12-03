'''Setup aws master-minion infrastrucuture and platform'''
import boto.ec2
import getpass
import logging
import os
import time
import json
import subprocess
import glob
from .config import get_platform_config, set_platform_config

logger = logging.getLogger()
logging.config.dictConfig({'version': 1, 'root': {'level': 'INFO'}})


def create_security_group(conn, name):
    groups = [g for g in conn.get_all_security_groups() if g.name == name]
    group = groups[0] if groups else None
    if not group:
        group = conn.create_security_group(name, 'This is {}'.format(name))
        group.authorize(ip_protocol='tcp',
                        from_port=str(22),
                        to_port=str(22),
                        cidr_ip='0.0.0.0/0')
        group.authorize(ip_protocol='tcp',
                        from_port=str(80),
                        to_port=str(80),
                        cidr_ip='0.0.0.0/0')
        group.authorize(ip_protocol='tcp',
                        from_port=str(443),
                        to_port=str(443),
                        cidr_ip='0.0.0.0/0')
    return group


def create_ec2(conn, group_name, keypair_name):
    reservation = conn.run_instances(image_id='ami-00b11177',
                                     key_name=keypair_name,
                                     security_groups=[group_name],
                                     instance_type='t1.micro')
    running_instance = reservation.instances[0]
    status = running_instance.update()
    while status == 'pending':
        logger.info('waiting 10 secs for the instance to come up...')
        time.sleep(10)
        status = running_instance.update()
    addr = conn.allocate_address()
    addr.associate(running_instance.id)
    return addr.public_ip


def _sync_salt(host, key_path):
    for src, dst in [("salt/roots/", "/srv/salt"),
                     ("salt/pillar/", "/srv/pillar")]:
        cmd = ['rsync', '-avz',
               '--exclude', 'dist',
               '-e', 'ssh -l ubuntu -i {}'.format(key_path),
               src.rstrip('/') + '/',
               '{}:///{}/'.format(host, dst)
           ]
        subprocess.check_call(cmd)


def sync_salt():
    config = get_platform_config()
    _sync_salt(config['master']['ip'], config['master']['keypair'])


def _provision(host, key_path):
    # TODO: add standalone mode arg
    for dir_ in ('/srv/salt', '/srv/pillar'):
        subprocess.check_call(
            'ssh -i {key} ubuntu@{host} sudo bash -c '
            '"mkdir {dir}; chown ubuntu:ubuntu {dir}"'
            .format(key=key_path, host=host, dir=dir_).split()
        )
    _sync_salt(host, key_path)
    subprocess.check_call(
        'scp -i {key} {script} ubuntu@{host}:/tmp/provision.py'.format(
            key=key_path,
            host=host,
            script=os.path.join(os.path.dirname(__file__), 'provision.py')
        ).split()
    )
    subprocess.check_call(
        'ssh -i {key} ubuntu@{host} sudo /tmp/provision.py --no-standalone'.format(
            key=key_path,
            host=host
        ).split()
    )


def provision():
    config = get_platform_config()
    _provision(config['master']['ip'], config['master']['keypair'])


def bootstrap():
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    if not access_key:
        access_key = input('AWS access key: ')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    if not secret_key:
        secret_key = getpass.getpass('AWS secret key: ')
    conn = boto.ec2.connect_to_region('eu-west-1',
                                      aws_access_key_id=access_key,
                                      aws_secret_access_key=secret_key)

    group_name = 'testg'
    group = create_security_group(conn, group_name)
    key_name = 'testk6'
    key_path = os.path.join('.secrets', '{}.pem'.format(key_name))
    try:
        key = conn.create_key_pair(key_name)
    except boto.exception.EC2ResponseError:
        # Key exists
        logger.info('using existing access key {} that shoud be in {}'.format(
            key_name, key_path))
    else:
        os.umask(0x077)
        with open(key_path, 'w') as f:
            f.write(key.material)

    public_ip = create_ec2(conn, group_name, key_name)
    config = {
        'master': {'ip': public_ip, 'keypair': key_path}
    }
    set_platform_config(config)
    conn.close()
    provision()
