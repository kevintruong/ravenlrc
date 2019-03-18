#!/usr/bin/env bash
sudo sed -i 's/http\:\/\/archive\.ubuntu\.com\/ubuntu/http\:\/\/free\.nchc\.org\.tw\/ubuntu\//g' /etc/apt/sources.list && \
	apt-get update && apt-get upgrade --yes
sudo apt-get update
sudo apt-get install -y --no-install-recommends python3-setuptools python3 ffmpeg  \
    software-properties-common \
    software-properties-common python3-pip openssh-server &&\
    pip3 install wheel &&\
    pip3 install hug --upgrade
sudo add-apt-repository ppa:jonathonf/ffmpeg-4 && apt install -y ffmpeg
sudo add-apt-repository ppa:alessandro-strada/ppa && \
    apt-get install -y google-drive-ocamlfuse

sudo wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get -y update
sudo apt-get install -y google-chrome-stable

# install chromedriver
sudo apt-get install -yqq unzip
sudo wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
sudo unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

