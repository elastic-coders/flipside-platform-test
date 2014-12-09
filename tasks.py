from invoke import ctask as task, run, Collection
import os
import json
import subprocess
import shutil

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
        # XXX ???
        import flipside_platform.aws
        flipside_platform.aws.bootstrap()
        flipside_platform.aws.provision()
        # ctx.run('docker run -it --rm -v {pwd}/.secrets:/.secrets '
        #         'elasticcoders/platform-test python3 -m flipside_platform.aws flipside_platform.aws'.format(
        #             pwd=os.path.abspath(os.curdir)),
        #         pty=True)
    elif target == 'vagrant':
        ctx.run('vagrant up --provision')
    else:
        import provision
        provision.main()


@task
def platform_provision(ctx, target):
    if target == 'aws':
        # XXX ???
        import flipside_platform.aws
        flipside_platform.aws.provision()
        # ctx.run('docker run -it --rm -v {pwd}/.secrets:/.secrets '
        #         'elasticcoders/platform-test python3 -m flipside_platform.aws flipside_platform.aws'.format(
        #             pwd=os.path.abspath(os.curdir)),
        #         pty=True)
    elif target == 'vagrant':
        ctx.run('vagrant provision')
    else:
        assert False


@task
def platform_ssh(ctx, target, args=None):
    if target == 'aws':
        config = get_platform_config()
        cmd = ['ssh', 'ssh', '-i', config['master']['keypair'],
               'ubuntu@{}'.format(config['master']['ip'])]
    elif target == 'vagrant':
        cmd = ['vagrant', 'vagrant', 'ssh', '--']
    else:
        print('crazy stuff')
        return
    if args:
        cmd.extend(args)
    os.execlp(*cmd)


@task
def platform_sync(ctx, target):
    if target == 'aws':
        sync_salt()
    elif target == 'vagrant':
        print('vagrant is automatically synced through shared folders')
    else:
        print('crazy stuff')



@task
def app_create(ctx, target, name):
    # XXX is this really necessary?
    platform_ssh(ctx, target, ['mkdir', '-p', '/srv/salt/dist/{}'.format(name)])


@task
def app_publish(ctx, target, name, archive, tag='master'):
    archive_name_in_host = '{name}/{tag}'.format(tag=tag, name=name)
    if target == 'aws':
        config = get_platform_config()
        cmd = ['rsync', '-avz', '-e',
               'ssh -l ubuntu -i {}'.format(config['master']['keypair']),
               archive.rstrip('/') + '/',
               '{}:///srv/salt/dist/{}/'.format(config['master']['ip'],
                                                archive_name_in_host)
           ]
        subprocess.check_call(cmd)
    elif target == 'vagrant':
        # TODO use rsync
        dst_dir = '.dist/{}'.format(archive_name_in_host)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        shutil.rmtree(dst_dir)
        shutil.copytree(archive, dst_dir)
        platform_ssh(ctx, target, [
            'cp',
            '-r',
            '/vagrant/.dist/{}'.format(name),
            '/srv/salt/dist'])


@task
def app_deploy(ctx, target, name, tag='master'):
    platform_ssh(ctx, target, ['sudo', '-H', 'salt-call', 'state.highstate'])



platform = Collection('platform')
platform.add_task(platform_bootstrap, 'bootstrap')
platform.add_task(platform_ssh, 'ssh')
platform.add_task(platform_sync, 'sync')
platform.add_task(platform_provision, 'provision')

app = Collection('app')
app.add_task(app_create, 'create')
app.add_task(app_publish, 'publish')
app.add_task(app_deploy, 'deploy')

ns = Collection()
ns.add_collection(platform)
ns.add_collection(app)
ns.add_collection(docker)
