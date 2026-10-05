import {handleApi} from '../sandbox/api.mjs';
const evidence = {"query": {"source": "Native Prometheus 3.5.0", "method": "POST", "path": "/api/v1/query", "request": {"query": "vector(1)", "time": "1791187200"}, "status": 200, "payload": {"status": "success", "data": {"resultType": "vector", "result": [{"metric": {}, "value": [1791187200, "1"]}]}}}, "query_range": {"source": "Native Prometheus 3.5.0", "method": "POST", "path": "/api/v1/query_range", "request": {"query": "vector(1)", "start": "1791187200", "end": "1791187230", "step": "15s"}, "status": 200, "payload": {"status": "success", "data": {"resultType": "matrix", "result": [{"metric": {}, "values": [[1791187200, "1"], [1791187215, "1"], [1791187230, "1"]]}]}}}, "series": {"source": "Native Prometheus 3.5.0", "method": "POST", "path": "/api/v1/series", "request": {"match[]": "up{job=\"prometheus\"}"}, "status": 200, "payload": {"status": "success", "data": [{"__name__": "up", "instance": "127.0.0.1:9095", "job": "prometheus"}]}}, "labels": {"source": "Native Prometheus 3.5.0", "method": "POST", "path": "/api/v1/labels", "request": {"match[]": "up{job=\"prometheus\"}"}, "status": 200, "payload": {"status": "success", "data": ["__name__", "instance", "job"]}}, "format_query": {"source": "Native Prometheus 3.5.0", "method": "POST", "path": "/api/v1/format_query", "request": {"query": "sum( up{job=\"prometheus\"} )"}, "status": 200, "payload": {"status": "success", "data": "sum(up{job=\"prometheus\"})"}}, "query_invalid": {"source": "Native Prometheus 3.5.0", "method": "POST", "path": "/api/v1/query", "request": {"query": "sum("}, "status": 400, "payload": {"status": "error", "errorType": "bad_data", "error": "invalid parameter \"query\": 1:5: parse error: unclosed left parenthesis"}}};
// Reuse the same laboratory API for the Vercel Node.js runtime.
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const originalPath = url.searchParams.get('lab_path');
    if (originalPath) {
      url.pathname = originalPath;
      url.searchParams.delete('lab_path');
      request = new Request(url, request);
    }
    return await handleApi(request, evidence) || new Response('Not found', {status:404});
  }
};
