# Flipside platform spike

**This is a work in progress. currently almost nothing works What follows
is more like a set of goals.**

Easily host a python web application.

Platform is orchestrated using Salt Stack and can be boostrapped easily on a
vagrant-managed local VM and on AWS.

Developer automation is managed by Docker.

Single-machine setup that includes:
- salt master & minion
- frontend nginx web server
- memcache server
- log rotation
- rsyslog centralized logging (with optional logentries passthrough)
- aws cloudwatch monitoring
- One or more application containers:
 - uwsgi
 - support for hot and cold restart (uwsgi chain reloading)
 - configuration through env var files (managed trough salt "secret" pillars)
 - automation for running applications both locally and remotely
 - templates:
  - A python/django/sqlite stack:
   - python/django
   - sqlite database dir
   - connects to the local memcache
   - incremental & encrypted backup and restore of sqlite databases
   - integration with buildbot CI

Each application consists of:
 - a name
 - a deploy template (currently only `python-django-sqlite` is implemented)
 - deploy template options (nginx config, static assets...)
 - code package (python wheel)
 - runtime configuration (environment variables)

**TODO**:
 - graphite stats
 - monitoring

**LIMITATION** for now it can run stuff on a single machine only


## Developer environment setup

0. make sure you have ubuntu 14.04
1. install docker
2. authenticate into docker hub with `sudo docker login`
3. install python3 and pip with `sudo apt-get install python3 python3-pip`
4. install invoke running `sudo pip install invoke`



## Bootstrap platform

Creates a single machine hosting the salt master, salt minion and provisions it.

Run `invoke platform.bootstrap --target=[aws | host | vagrant]`

AWS:
 - enter your AWS credentials when asked

you can login the master machine with `invoke platform.ssh [target]`


a `.flipside-platform` file is created in the current dir with all the config.


## Develop a flipside app

Boostrap the app running:

    invoke app.bootstrap <name> -d <app dir> -t python-django-sqlite

A `.flipside-app` is created in the current dir.

Publish the app version with `invoke app.publish [name]`

TODO: Test the app running `invoke app.test <name>`

Deploy the version with `invoke app.deploy <name> --tag latest`
