#!/bin/sh
# Evaluate a range query. Run npm start before this request.
set -eu
curl --fail-with-body -sS \
  -u 'labreader:prometheus-lab-demo' \
  'http://127.0.0.1:8085/sandbox/prometheus/api/v1/query_range' \
  --data-urlencode 'query=vector(1)' \
  --data-urlencode 'start=1791187200' \
  --data-urlencode 'end=1791187230' \
  --data-urlencode 'step=15s'
