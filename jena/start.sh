#!/bin/bash

DIR=$(dirname "$0")
~/.local/bin/podman-compose -f "${DIR}/../docker-compose.yml" up --force-recreate fuseki
