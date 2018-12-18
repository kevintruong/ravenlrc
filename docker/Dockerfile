FROM ubuntu:18.04

#run apt update and install all uefi components
RUN apt-get update
RUN apt-get install -y --no-install-recommends python3-setuptools python3 python3-pip &&\
    pip3 install wheel &&\
    pip3 install hug --upgrade
#RUN    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /tmp/ytcreator
WORKDIR /tmp/ytcreator
EXPOSE 30000
CMD []
