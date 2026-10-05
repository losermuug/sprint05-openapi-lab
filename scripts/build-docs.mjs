import {mkdirSync, copyFileSync, readFileSync, writeFileSync, readdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {resolve, join} from 'node:path';
const base=resolve('.');
mkdirSync('public/vendor',{recursive:true});
for (const file of ['swagger-ui-bundle.js','swagger-ui-standalone-preset.js','swagger-ui.css'])
  copyFileSync(`node_modules/swagger-ui-dist/${file}`,`public/vendor/${file}`);
copyFileSync('node_modules/redoc/bundles/redoc.standalone.js','public/vendor/redoc.standalone.js');
writeFileSync('public/swagger/index.html', `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Swagger UI Laboratory</title><link rel="stylesheet" href="/vendor/swagger-ui.css"><style>body{margin:0}nav{padding:16px 32px;font:16px system-ui;background:#122134;color:white}nav a{color:#b8dbff;margin-right:24px}.topbar{background:#122134}</style></head><body><nav><a href="/">Lab home</a><a href="/redoc/">Redoc</a>Training sandbox · Basic: labreader / prometheus-lab-demo · Bearer: corgly-lab-einstein-2026</nav><div id="swagger-ui"></div><script src="/vendor/swagger-ui-bundle.js"></script><script src="/vendor/swagger-ui-standalone-preset.js"></script><script>window.ui=SwaggerUIBundle({urls:[{url:'/openapi.yaml',name:'Prometheus five endpoints'},{url:'/corgly.yaml',name:'Corg.ly UE-5'}],dom_id:'#swagger-ui',deepLinking:true,filter:true,validatorUrl:null,layout:'StandaloneLayout',presets:[SwaggerUIBundle.presets.apis,SwaggerUIStandalonePreset]});</script></body></html>`);
for (const [spec,target] of [['openapi.yaml','index.html'],['corgly.yaml','corgly.html']]) {
  const result=spawnSync(process.execPath,['node_modules/@redocly/cli/bin/cli.js','build-docs',`docs/openapi/${spec}`,'-o',`public/redoc/${target}`],{encoding:'utf8'});
  process.stdout.write(result.stdout);process.stderr.write(result.stderr);
  if(result.status!==0)process.exit(result.status||1);
  const file=`public/redoc/${target}`;
  writeFileSync(file,readFileSync(file,'utf8')
    .replace('https://cdn.redocly.com/redoc/v2.5.1/bundles/redoc.standalone.js','/vendor/redoc.standalone.js')
    // Avoid SSR/client hydration mismatch for relative servers and dynamic viewport.
    .replace('Redoc.hydrate(__redoc_state, container);',
      "container.replaceChildren(); Redoc.init(__redoc_state.spec.data, __redoc_state.options, container);"));
}
mkdirSync('dist/server',{recursive:true});
const assets={};
const types={html:'text/html; charset=utf-8',js:'text/javascript',css:'text/css',yaml:'application/yaml',md:'text/plain; charset=utf-8',json:'application/json',png:'image/png',wav:'audio/wav'};
function collect(dir,relative='') {
  for(const entry of readdirSync(dir,{withFileTypes:true})) {
    const key=join(relative,entry.name);
    if(entry.isDirectory())collect(join(dir,entry.name),key);
    else assets['/'+key]={type:types[entry.name.split('.').at(-1)]||'application/octet-stream',body:readFileSync(join(dir,entry.name)).toString('base64')};
  }
}
collect('public');
const evidence={};
for(const key of ['query','query_range','series','labels','format_query','query_invalid'])
  evidence[key]=JSON.parse(readFileSync(`docs/evidence/${key}.json`));
const api=readFileSync('sandbox/api.mjs','utf8');
writeFileSync('dist/server/index.js',api+'\nconst evidence='+JSON.stringify(evidence)+';\nconst assets='+JSON.stringify(assets)+`;\nexport default {async fetch(request){const api=await handleApi(request,evidence);if(api)return api;let path=new URL(request.url).pathname;if(path.endsWith('/'))path+='index.html';const asset=assets[path];if(!asset)return new Response('Not found',{status:404});return new Response(Uint8Array.from(atob(asset.body),char=>char.charCodeAt(0)),{headers:{'Content-Type':asset.type}});}};\n`);
console.log(`Built ${Object.keys(assets).length} local assets and the Cloudflare Worker.`);
