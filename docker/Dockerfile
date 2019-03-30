FROM ubuntu:18.04

#run apt update and install all uefi components
RUN sed -i 's/http\:\/\/archive\.ubuntu\.com\/ubuntu/http\:\/\/free\.nchc\.org\.tw\/ubuntu\//g' /etc/apt/sources.list && \
	apt-get update && apt-get upgrade --yes
RUN apt-get update
RUN apt-get install -y --no-install-recommends python3-setuptools python3 ffmpeg  \
    software-properties-common \
    software-properties-common python3-pip openssh-server &&\
    pip3 install wheel &&\
    pip3 install hug --upgrade
RUN apt install -y gcc python3-dev
RUN add-apt-repository ppa:jonathonf/ffmpeg-4 && apt install -y ffmpeg
RUN mkdir -p /tmp/ytcreator
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt --upgrade
RUN apt-get install -y locales
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
WORKDIR /tmp/ytcreator
EXPOSE 8000
ENTRYPOINT hug -f backendapi.py
#ENTRYPOINT bash
