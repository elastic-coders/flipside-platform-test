'''Setup aws master-minion infrastrucuture and platform'''


def create_ec2():
    pass


def create_iam():
    pass


def provision():
    host = 'ubuntu@{}'.format(ciao)
    run('scp provision.py {}/tmp'.format(host))
    run('ssh {} provision.py'.forma(host))


def main():
    create_ec2()
    create_iam()
    provision()


if __name__ == '__main__':
    main()
