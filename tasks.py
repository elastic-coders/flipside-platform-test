from invoke import ctask as task, run, Collection
import os
import json


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
def platform_ssh(ctx, target):
    if target == 'aws':
        with open('.flipside-config.json', 'r') as f:
            data = json.load(f)
        os.execlp('ssh', 'ssh', '-i', data['master']['keypair'],
                  'ubuntu@{}'.format(data['master']['ip']))
    elif target == 'vagrant':
        os.execlp('vagrant', 'vagrant', 'ssh')
    else:
        print('crazy stuff')


platform = Collection('platform')
platform.add_task(platform_bootstrap, 'bootstrap')
platform.add_task(platform_ssh, 'ssh')

ns = Collection()
ns.add_collection(platform)
ns.add_collection(docker)
