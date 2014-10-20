# Tools to bootstrap and manage a salt-based platform on AWS
FROM ubuntu:14.04
RUN apt-get -qq update
RUN apt-get -qqy install python3.4 python3-pip
RUN pip3 install awscli
RUN pip3 install boto
RUN pip3 install invoke

ADD . src
