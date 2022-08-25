#!/bin/bash

database="$1"
files="$2"

echo "importing data to database: ${database}"

/jena/bin/tdb2.tdbloader --loc "${FUSEKI_BASE}/databases/${database}" "${files}"/*
