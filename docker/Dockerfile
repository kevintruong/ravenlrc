FROM ubuntu:18.04
#RUN sed -i 's/http\:\/\/archive\.ubuntu\.com\/ubuntu/http\:\/\/free\.nchc\.org\.tw\/ubuntu\//g' /etc/apt/sources.list && \
RUN	apt-get update && apt-get upgrade --yes
RUN apt-get install -y --no-install-recommends python3 python3-pip python3-setuptools gcc python3-dev
RUN pip3 install --upgrade pip wheel
RUN mkdir -p /usr/share/render
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt --upgrade
WORKDIR /usr/share/render
CMD gunicorn --bind 0.0.0.0:$PORT --reload app:__hug_wsgi__


