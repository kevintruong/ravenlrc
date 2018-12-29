FROM ubuntu:18.04

#run apt update and install all uefi components
RUN apt-get update
RUN apt-get install -y --no-install-recommends python3-setuptools python3 \
    software-properties-common python3-pip openssh-server &&\
    pip3 install wheel &&\
    pip3 install hug --upgrade
#RUN    rm -rf /var/lib/apt/lists/*
RUN apt-get install -y --no-install-recommends vim

RUN mkdir /var/run/sshd
RUN echo 'root:testssh' | chpasswd &&\
#    echo 'PermitRootLogin yes' >>  /etc/ssh/sshd_config &&\
    echo "export VISIBLE=now" >> /etc/profile

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
RUN service ssh start
RUN mkdir -p /tmp/ytcreator
WORKDIR /tmp/ytcreator
EXPOSE 22
EXPOSE 8000
ENTRYPOINT service ssh restart && bash
