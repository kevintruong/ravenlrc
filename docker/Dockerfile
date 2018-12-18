FROM ubuntu:18.04

#run apt update and install all uefi components
RUN apt-get update
RUN apt-get install -y --no-install-recommends python3-setuptools python3 python3-pip openssh-server &&\
    pip3 install wheel &&\
    pip3 install hug --upgrade
#RUN    rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd
RUN echo 'root:testssh' | chpasswd &&\
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config &&\
    sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd &&\
    echo "export VISIBLE=now" >> /etc/profile
RUN system

RUN mkdir -p /tmp/ytcreator
WORKDIR /tmp/ytcreator

EXPOSE 22
EXPOSE 8000
CMD []
