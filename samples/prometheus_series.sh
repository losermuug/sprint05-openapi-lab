#!/bin/sh
# Find matching series. Run npm start before this request.
set -eu
curl --fail-with-body -sS \
  -u 'labreader:prometheus-lab-demo' \
  'http://127.0.0.1:8085/sandbox/prometheus/api/v1/series' \
  --data-urlencode 'match[]=up{job="prometheus"}'
