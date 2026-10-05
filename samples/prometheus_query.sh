#!/bin/sh
# Evaluate an instant query. Run npm start before this request.
set -eu
curl --fail-with-body -sS \
  -u 'labreader:prometheus-lab-demo' \
  'http://127.0.0.1:8085/sandbox/prometheus/api/v1/query' \
  --data-urlencode 'query=vector(1)' \
  --data-urlencode 'time=1791187200'
