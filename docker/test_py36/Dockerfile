FROM debian:stretch

MAINTAINER Summer Babe <mksh@null.net>

RUN apt-get update
RUN apt-get install -y --force-yes zlib1g zlib1g-dev build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev git
RUN curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
RUN /root/.pyenv/bin/pyenv install 3.6.1
RUN /root/.pyenv/versions/3.6.1/bin/python -m pip install nose asynctest nose-cov
ADD . /opt/aiobasex/
WORKDIR /opt/aiobasex/
ENTRYPOINT ["/root/.pyenv/versions/3.6.1/bin/python", "-m", "nose", "-sv", "--nologcapture", "aiobasex.test", "--with-cov", "--cov=aiobasex", "--cov-report=term-missing"]
