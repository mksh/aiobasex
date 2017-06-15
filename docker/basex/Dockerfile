#
# This code was borrowed from BaseX source, and contains slight modifications.
#

FROM debian:stretch

MAINTAINER Summer Babe <mksh@null.net>

RUN apt-get update
RUN apt-get install -y --force-yes git build-essential openjdk-8-jdk openjdk-8-jre maven
RUN git clone https://github.com/BaseXdb/basex /usr/local/src/basex

# Compile BaseX, install
RUN cd /usr/local/src/basex && \
    mvn clean install -DskipTests && \
    ln -s /usr/local/src/basex/basex-*/etc/* /usr/local/bin && \
    cp -r /usr/local/src/basex/basex-api/src/main/webapp/WEB-INF /srv

# Run as non-privileged user with fixed UID
# $MAVEN_CONFIG is expected to point to a volume by the parent maven image
RUN adduser --home /srv --disabled-password --disabled-login --uid 1984 basex && \
    mkdir /srv/.m2 /srv/BaseXData /srv/BaseXRepo /srv/BaseXWeb && \
    chown -R basex /srv
USER basex
ENV MAVEN_CONFIG=/srv/.m2

# 1984/tcp: API
# 8984/tcp: HTTP
# 8985/tcp: HTTP stop
EXPOSE 1984 8984 8985
VOLUME ["/srv/.m2", "/srv/BaseXData"]
WORKDIR /srv

# Run BaseX API server by default
CMD ["/usr/local/bin/basexserver", "-d"]
