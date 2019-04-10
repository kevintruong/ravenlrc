FROM ubuntu:18.04

#RUN sed -i 's/http\:\/\/archive\.ubuntu\.com\/ubuntu/http\:\/\/free\.nchc\.org\.tw\/ubuntu\//g' /etc/apt/sources.list && \
RUN	apt-get update && apt-get upgrade --yes
RUN apt-get install -y --no-install-recommends libgtk2.0-dev libboost-all-dev libluajit-5.1-dev libxxf86vm-dev  libsm6 libxext6 libice6
RUN mkdir -p /tmp/lyriceffect
WORKDIR /tmp/lyriceffect
COPY lyriceffect_generator.sh lyriceffect /usr/local/bin/
RUN chmod a+x /usr/local/bin/lyriceffect_generator.sh /usr/local/bin/lyriceffect
ENTRYPOINT ["lyriceffect"]
CMD []
