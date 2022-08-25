#!/bin/bash

cp "$FUSEKI_BASE/configuration/shiro.ini" "$FUSEKI_BASE/" 2>/dev/null
cp "$FUSEKI_BASE/configuration/config.ttl" "$FUSEKI_BASE/" 2>/dev/null

# fork 
exec "$@"
