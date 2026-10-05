"""Execute all shipped samples and validate actual HTTP payloads against OpenAPI."""
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
import requests
import yaml
from jsonschema import Draft4Validator, RefResolver

ROOT=Path(__file__).resolve().parents[1]
BASE=os.getenv('LAB_BASE_URL','http://127.0.0.1:8085').rstrip('/')
prom=yaml.safe_load((ROOT/'docs/openapi/openapi.yaml').read_text())
corg=yaml.safe_load((ROOT/'docs/openapi/corgly.yaml').read_text())
checks=[]

def record(name,condition):
    if not condition: raise AssertionError(name)
    checks.append({'name':name,'status':'PASS'})

def validate(payload,spec,operation,status):
    schema=operation['responses'][str(status)]['content']['application/json']['schema']
    Draft4Validator(schema,resolver=RefResolver.from_schema(spec)).validate(payload)

for key in ['query','query_range','series','labels','format_query']:
    evidence=json.loads((ROOT/f'docs/evidence/{key}.json').read_text())
    result=subprocess.run(['sh',str(ROOT/f'samples/prometheus_{key}.sh')],capture_output=True,text=True,check=True)
    payload=json.loads(result.stdout)
    validate(payload,prom,prom['paths'][f'/api/v1/{key}']['post'],200)
    record(f'Executable curl {key} and schema',payload==evidence['payload'])
    response=requests.post(f'{BASE}/sandbox/prometheus/api/v1/{key}',data=evidence['request'],auth=('labreader','prometheus-lab-demo'),timeout=10)
    validate(response.json(),prom,prom['paths'][f'/api/v1/{key}']['post'],200)
    record(f'HTTP {key} status and captured payload',response.status_code==200 and response.json()==evidence['payload'])
    unauth=requests.post(f'{BASE}/sandbox/prometheus/api/v1/{key}',data=evidence['request'],timeout=10)
    validate(unauth.json(),prom,prom['paths'][f'/api/v1/{key}']['post'],401)
    record(f'HTTP {key} rejects missing auth',unauth.status_code==401)

for key,path in [('upload_photo','/pets/upload-photo'),('translate_bark','/audio/translate-bark'),('subscribe_webhook','/webhooks/subscribe')]:
    env={**os.environ,'CORGLY_BASE_URL':BASE}
    result=subprocess.run([sys.executable,str(ROOT/f'samples/{key}.py')],env=env,capture_output=True,text=True,check=True)
    payload=json.loads(result.stdout)
    evidence=json.loads((ROOT/f'docs/evidence/{key}.json').read_text())
    validate(payload,corg,corg['paths'][path]['post'],evidence['status'])
    record(f'Executable Python {key} and schema',payload==evidence['payload'])
    unauth=requests.post(BASE+'/v1'+path,json={},timeout=10)
    validate(unauth.json(),corg,corg['paths'][path]['post'],401)
    record(f'Corg.ly {key} rejects missing auth',unauth.status_code==401)

invalid=requests.post(BASE+'/sandbox/prometheus/api/v1/query',data={'query':'sum('},auth=('labreader','prometheus-lab-demo'),timeout=10)
validate(invalid.json(),prom,prom['paths']['/api/v1/query']['post'],400)
record('Native bad PromQL capture matches sandbox',invalid.status_code==400 and invalid.json()==json.loads((ROOT/'docs/evidence/query_invalid.json').read_text())['payload'])
unsupported=requests.post(BASE+'/sandbox/prometheus/api/v1/query',data={'query':'up'},auth=('labreader','prometheus-lab-demo'),timeout=10)
record('Replay rejects unsupported input',unsupported.status_code==422)
auth={'Authorization':'Bearer corgly-lab-einstein-2026'}
photo=requests.post(BASE+'/v1/pets/upload-photo',headers=auth,data={'pet_id':'corgi_98231'},files={'photo':('einstein.txt',b'not a photo','text/plain')},timeout=10)
validate(photo.json(),corg,corg['paths']['/pets/upload-photo']['post'],415)
record('Photo rejects unsupported media type',photo.status_code==415)
audio=requests.post(BASE+'/v1/audio/translate-bark',headers=auth,data={'pet_id':'corgi_98231','language':'en'},files={'audio':('einstein.wav',b'invalid header','audio/wav')},timeout=10)
validate(audio.json(),corg,corg['paths']['/audio/translate-bark']['post'],400)
record('Audio rejects malformed WAV',audio.status_code==400)
hook=requests.post(BASE+'/v1/webhooks/subscribe',headers=auth,json={'pet_id':'corgi_98231','callback_url':'http://pet-owner.invalid/hook','events':['bark.translated']},timeout=10)
record('Webhook requires HTTPS',hook.status_code==400)
oversize=requests.post(BASE+'/v1/pets/upload-photo',headers=auth,data={'pet_id':'corgi_98231'},files={'photo':('einstein.png',b'x'*(2*1024*1024+1),'image/png')},timeout=10)
record('Upload rejects oversized body',oversize.status_code==413)
for spec in [prom,corg]:
    for path,item in spec['paths'].items():
        op=item['post']
        record(f'{path} has body and example',bool(op.get('requestBody')) and all('example' in content for content in op['requestBody']['content'].values()))
        record(f'{path} documents success and errors',any(code.startswith('2') for code in op['responses']) and any(code.startswith('4') for code in op['responses']) and any(code.startswith('5') for code in op['responses']))
report={'executed_at_utc':datetime.now(timezone.utc).isoformat(),'base_url':BASE,'passed':len(checks),'failed':0,'checks':checks,
        'not_fault_injected':['500','503'],'scope':'Training sandbox; native Prometheus captures are stored separately.'}
(ROOT/'docs/evidence/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'{len(checks)} checks passed; 8 runnable samples match their captured payloads and schemas.')
