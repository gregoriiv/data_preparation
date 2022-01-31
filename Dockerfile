FROM python:3.9

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# hadolint ignore=DL3008
RUN apt-get update --allow-releaseinfo-change -q && \
    apt-get install -q -y --no-install-recommends \
        bzip2 \
        ca-certificates \
        git \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        mercurial \
        openssh-client \
        procps \
        subversion \
        wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#Install osm2pgrouting
RUN cd /tmp/ && wget http://security.ubuntu.com/ubuntu/pool/universe/b/boost1.62/libboost-program-options1.62.0_1.62.0+dfsg-5_amd64.deb \
   && dpkg -i libboost-program-options1.62.0_1.62.0+dfsg-5_amd64.deb \
   && wget http://ftp.br.debian.org/debian/pool/main/o/osm2pgrouting/osm2pgrouting_2.2.0-1_amd64.deb \
   && dpkg -i osm2pgrouting_2.2.0-1_amd64.deb \
   && rm -rf /tmp/*


# Install Osmosis
RUN wget https://bretth.dev.openstreetmap.org/osmosis-build/osmosis-0.47.tgz \
    && mkdir osmosis \
    && mv osmosis-0.47.tgz osmosis \
    && cd osmosis \
    && tar xvfz osmosis-0.47.tgz \
    && rm osmosis-0.47.tgz \
    && chmod a+x bin/osmosis

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false


# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

WORKDIR /app

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

ENTRYPOINT ["tail"]
CMD ["-f","/dev/null"]

