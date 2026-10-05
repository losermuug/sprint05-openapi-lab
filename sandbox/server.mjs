import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {resolve, sep} from 'node:path';
import {handleApi} from './api.mjs';
const evidence = {};
for (const key of ['query','query_range','series','labels','format_query','query_invalid'])
  evidence[key] = JSON.parse(await readFile(new URL(`../docs/evidence/${key}.json`, import.meta.url)));
const root = resolve('public');
const types = {html:'text/html; charset=utf-8',js:'text/javascript',css:'text/css',yaml:'application/yaml',json:'application/json',png:'image/png',wav:'audio/wav',md:'text/plain; charset=utf-8'};
const server = createServer(async (incoming, outgoing) => {
  try {
    const chunks = [];
    for await (const chunk of incoming) {
      chunks.push(chunk);
      if (chunks.reduce((sum,item)=>sum+item.length,0) > 2 * 1024 * 1024) {
        outgoing.writeHead(413, {'Content-Type':'application/json'});
        outgoing.end(JSON.stringify({status:'error',errorType:'bad_data',error:'Maximum body size is 2 MiB.'})); return;
      }
    }
    const target = `http://127.0.0.1:${process.env.PORT || 8085}${incoming.url}`;
    const body = Buffer.concat(chunks);
    const request = new Request(target, {method:incoming.method, headers:incoming.headers,
      ...(body.length ? {body} : {})});
    const api = await handleApi(request, evidence);
    if (api) {outgoing.writeHead(api.status, Object.fromEntries(api.headers)); outgoing.end(Buffer.from(await api.arrayBuffer()));return;}
    let pathname = decodeURIComponent(new URL(target).pathname);
    if (pathname.endsWith('/')) pathname += 'index.html';
    const file = resolve(root, '.' + pathname);
    if (!file.startsWith(root + sep)) {outgoing.writeHead(403);outgoing.end();return;}
    const contents = await readFile(file);
    outgoing.writeHead(200, {'Content-Type':types[file.split('.').at(-1)] || 'application/octet-stream'});
    outgoing.end(contents);
  } catch { outgoing.writeHead(404); outgoing.end('Not found'); }
});
server.listen(Number(process.env.PORT || 8085), '127.0.0.1', () => console.log('Lab server: http://127.0.0.1:8085'));
