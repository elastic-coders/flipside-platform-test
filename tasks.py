from invoke import ctask as task, run, Collection
import os


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


platform = Collection('platform')
platform.add_task(platform_bootstrap, 'bootstrap')

ns = Collection()
ns.add_collection(platform)
ns.add_collection(docker)
