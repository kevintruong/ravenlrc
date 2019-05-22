FROM ubuntu:18.04

#RUN sed -i 's/http\:\/\/archive\.ubuntu\.com\/ubuntu/http\:\/\/free\.nchc\.org\.tw\/ubuntu\//g' /etc/apt/sources.list && \
RUN	apt-get update && apt-get upgrade --yes
RUN apt-get install -y --no-install-recommends python3 python3-pip python3-setuptools gcc python3-dev locales
RUN apt-get install -y libmediainfo-dev
RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
RUN pip3 install --upgrade pip wheel
RUN mkdir -p /usr/share/render
ARG deploy_env='product'
COPY requirements.txt /tmp/
ENV DEPLOY_ENV=$deploy_env
EXPOSE 5000/tcp
RUN pip3 install -r /tmp/requirements.txt --upgrade
COPY . /usr/share/render
WORKDIR /usr/share/render
CMD gunicorn --bind 0.0.0.0:5000 --reload app:__hug_wsgi__ --timeout 300 --workers=1 --threads=10


