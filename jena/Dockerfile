#   Licensed to the Apache Software Foundation (ASF) under one or more
#   contributor license agreements.  See the NOTICE file distributed with
#   this work for additional information regarding copyright ownership.
#   The ASF licenses this file to You under the Apache License, Version 2.0
#   (the "License"); you may not use this file except in compliance with
#   the License.  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


FROM openjdk:19-jdk-alpine

ENV LANG C.UTF-8
# RUN set -eux; \
#     apt-get update; \
#     apt-get install -y --no-install-recommends \
#        bash curl ca-certificates findutils coreutils gettext pwgen procps tini \
#     ; \
#     rm -rf /var/lib/apt/lists/*
RUN apk --no-cache add bash curl ca-certificates


ENV JENA_SOURCE http://archive.apache.org/dist/jena/binaries
ENV VERSION 4.5.0
ENV JENA_SHA512 84e23ca41e8e38b286abf769d3ccdfe069f6157d58e0bb24e78d98ed5f8d598e06ededc16dd5bde0a494d5ee7c49ab9c4f5335cf63727a302e6b8b929d47457f
ENV FUSEKI_SHA512 1d60d596a4aa6f3c786e0da86190e406152ed2f5e0698960c6065a0b85bef5bde9844771ddb7cb22aefd95e38c1510ae4ac4d089a484211edc167080ec3af452
# Config and data
ENV JENA_HOME /jena
ENV FUSEKI_BASE /fuseki
ENV FUSEKI_HOME /jena-fuseki

# Installation folder

WORKDIR /tmp

# published sha512 checksum
RUN echo "$JENA_SHA512  jena.tar.gz" > jena.tar.gz.sha512
# Download/check/unpack/move in one go (to reduce image size)
RUN curl --location --silent --show-error --fail --retry-connrefused --retry 3 --output jena.tar.gz ${JENA_SOURCE}/apache-jena-$VERSION.tar.gz && \
    sha512sum -c jena.tar.gz.sha512 && \
    tar zxf jena.tar.gz && \
    mv apache-jena* $JENA_HOME && \
    rm jena.tar.gz* && \
    cd $JENA_HOME && chmod 755 bin/*

# published sha512 checksum
RUN echo "$FUSEKI_SHA512  fuseki.tar.gz" > fuseki.tar.gz.sha512
# Download/check/unpack/move in one go (to reduce image size)
RUN curl --location --silent --show-error --fail --retry-connrefused --retry 3 --output fuseki.tar.gz ${JENA_SOURCE}/apache-jena-fuseki-$VERSION.tar.gz && \
    sha512sum -c fuseki.tar.gz.sha512 && \
    tar zxf fuseki.tar.gz && \
    mv apache-jena-fuseki* $FUSEKI_HOME && \
    rm fuseki.tar.gz* && \
    cd $FUSEKI_HOME && chmod 755 fuseki-server

# Test the install by testing it's ping resource. 20s sleep because Docker Hub.
RUN $FUSEKI_HOME/fuseki-server & \
    sleep 2 && \
    curl -sS --fail 'http://localhost:3030/$/ping' 

# No need to kill Fuseki as our shell will exit after curl

COPY docker-entrypoint.sh /
RUN chmod 755 /docker-entrypoint.sh


COPY bulk_import.sh $FUSEKI_HOME/
RUN chmod 755 $FUSEKI_HOME/bulk_import.sh


# Where we start our server from
WORKDIR $FUSEKI_HOME

# Make sure we start with empty /fuseki
RUN rm -rf $FUSEKI_BASE
VOLUME $FUSEKI_BASE

EXPOSE 3030
ENTRYPOINT ["/bin/sh", "--", "/docker-entrypoint.sh"]
CMD ["/jena-fuseki/fuseki-server"]

