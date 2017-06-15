FROM debian:stretch

MAINTAINER Summer Babe <mksh@null.net>

RUN apt-get update
RUN apt-get install -y --force-yes python3-dev python3-pip

RUN python3 -m pip install nose asynctest nose-cov
ADD . /opt/aiobasex/
WORKDIR /opt/aiobasex/
ENTRYPOINT ["python3.5", "-m", "nose", "-sv", "--nologcapture", "aiobasex.test", "--with-cov", "--cov=aiobasex", "--cov-report=term-missing"]
