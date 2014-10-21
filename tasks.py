from invoke import ctask as task, run, Collection
import os
import json
from flipside_platform.config import get_platform_config
from flipside_platform.aws import sync_salt


@task
def docker_build(ctx):
    ctx.run('docker build -t elasticcoders/platform-test .', pty=True)


@task
def docker_push(ctx):
    ctx.run('docker push elasticcoders/platform-test', pty=True)

docker = Collection('docker')
docker.add_task(docker_build, 'build')
docker.add_task(docker_push, 'push')


@task
def platform_bootstrap(ctx, target):
    '''Bootstrap the platform on different infrastructure types.'''
    if target == 'aws':
        ctx.run('docker run -it --rm -v {pwd}/.secrets:/.secrets '
                'elasticcoders/platform-test python3 bootstrap_aws.py'.format(
                    pwd=os.path.abspath(os.curdir)),
                pty=True)
    elif target == 'vagrant':
        ctx.run('vagrant up --provision')
    else:
        import provision
        provision.main()


@task
def platform_ssh(ctx, target, args=None):
    if target == 'aws':
        config = get_platform_config()
        os.execlp('ssh', 'ssh', '-i', config['master']['keypair'],
                  'ubuntu@{}'.format(config['master']['ip']))
    elif target == 'vagrant':
        os.execlp('vagrant', 'vagrant', 'ssh')
    else:
        print('crazy stuff')


@task
def platform_sync(ctx, target):
    if target == 'aws':
        sync_salt()
    elif target == 'vagrant':
        print('vagrant is automatically synced through shared folders')
    else:
        print('crazy stuff')



platform = Collection('platform')
platform.add_task(platform_bootstrap, 'bootstrap')
platform.add_task(platform_ssh, 'ssh')
platform.add_task(platform_sync, 'sync')

ns = Collection()
ns.add_collection(platform)
ns.add_collection(docker)
