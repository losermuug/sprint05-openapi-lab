"""Build 3.0.3 contracts from captured server payloads, never handwritten replies."""
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidence'
ORIGIN = 'https://sprint05-openapi-lab.vercel.app'

def ref(name):
    return {'$ref': f'#/components/schemas/{name}'}

def capture(name):
    return json.loads((EVIDENCE / f'{name}.json').read_text())

def infer(value):
    if isinstance(value, bool):
        return {'type': 'boolean'}
    if isinstance(value, int):
        return {'type': 'integer'}
    if isinstance(value, float):
        return {'type': 'number'}
    if isinstance(value, str):
        return {'type': 'string'}
    if isinstance(value, list):
        return {'type': 'array', 'items': infer(value[0]) if value else {'type': 'string'}}
    return {'type': 'object', 'required': list(value), 'properties': {k: infer(v) for k,v in value.items()}, 'additionalProperties': False}

ERROR = {'type':'object','required':['status','errorType','error'],'properties':{
    'status':{'type':'string','enum':['error']},'errorType':{'type':'string'},'error':{'type':'string'}}}

def errors():
    return {str(code): {'description':description,'content':{'application/json':{'schema':ref('ErrorResponse')}}}
            for code,description in [(400,'Invalid or missing inputs.'),(401,'Missing or invalid laboratory credentials.'),
              (422,'Unsupported sandbox input or failed query execution.'),(503,'Query timeout or upstream unavailable.')]} 

def base(title, description, server, security):
    return {'openapi':'3.0.3','info':{'title':title,'version':'1.0.0','description':description,
        'license':{'name':'Apache-2.0','url':'https://www.apache.org/licenses/LICENSE-2.0'},
        'contact':{'name':'SWPD laboratory'}},
        'servers':[{'url':server,'description':'Same-origin training sandbox'}],
        'security':[{security:[]}], 'paths':{},'components':{'schemas':{'ErrorResponse':ERROR},'securitySchemes':{}}}

prom = base('Prometheus Query API Laboratory',
    'Five native Prometheus 3.5.0 POST interfaces. The hosted server is a replay sandbox, not a PromQL engine. '
    'Use the exact request examples. Basic credentials labreader / prometheus-lab-demo are public demo credentials. '
    'Native upstream captures were taken on 127.0.0.1:9095 without authentication; BasicAuth belongs to the laboratory gateway. '
    'Gateway 401 is JSON. Native 503 is documented but was not fault-injected.', '/sandbox/prometheus', 'BasicAuth')
prom['components']['securitySchemes']['BasicAuth'] = {'type':'http','scheme':'basic','description':'Laboratory gateway only: labreader / prometheus-lab-demo. Use HTTPS outside loopback.'}
prom['tags'] = [{'name':'Queries','description':'Evaluate and format PromQL expressions.'},
                {'name':'Metadata','description':'Find time series and label names.'}]
metric = {'type':'object','additionalProperties':{'type':'string'}}
sample_pair = {'type':'array','minItems':2,'maxItems':2,'description':'A Unix timestamp followed by a string-encoded sample value.',
               'items':{'oneOf':[{'type':'number'},{'type':'string'}]}}
vector_item = {'type':'object','required':['metric','value'],'properties':{'metric':ref('MetricLabels'),'value':ref('SamplePair')}}
matrix_item = {'type':'object','required':['metric','values'],'properties':{'metric':ref('MetricLabels'),'values':{'type':'array','items':ref('SamplePair')}}}
prom['components']['schemas'].update({'MetricLabels':metric,'SamplePair':sample_pair,'VectorSeries':vector_item,'MatrixSeries':matrix_item})
settings = [
 ('query','Evaluate an instant query','Queries','QueryResponse','vector'),
 ('query_range','Evaluate a range query','Queries','RangeResponse','matrix'),
 ('series','Find matching series','Metadata','SeriesResponse',None),
 ('labels','List matching label names','Metadata','LabelsResponse',None),
 ('format_query','Format a PromQL expression','Queries','FormatResponse',None)]
for key,title,tag,schema_name,result_type in settings:
    record = capture(key)
    if result_type:
        data = {'type':'object','required':['resultType','result'],'properties':{
            'resultType':{'type':'string','enum':[result_type]},'result':{'type':'array','items':ref('VectorSeries' if result_type=='vector' else 'MatrixSeries')}}}
    elif key=='series':
        data = {'type':'array','items':ref('MetricLabels')}
    elif key=='labels':
        data = {'type':'array','items':{'type':'string'}}
    else:
        data = {'type':'string'}
    prom['components']['schemas'][schema_name] = {'type':'object','required':['status','data'],'properties':{
        'status':{'type':'string','enum':['success']},'data':data,
        'warnings':{'type':'array','items':{'type':'string'}},'infos':{'type':'array','items':{'type':'string'}}},'example':record['payload']}
    properties = {k: {'type':'string','description':{
        'query':'PromQL expression.','time':'Unix timestamp in seconds or RFC3339.','start':'Inclusive start timestamp.',
        'end':'Inclusive end timestamp.','step':'Resolution, for example 15s.','match[]':'Prometheus series selector; this field can repeat.'}[k],
        'example':v} for k,v in record['request'].items()}
    if 'match[]' in properties:
        properties['match[]']={'type':'array','items':{'type':'string'},'description':'Repeated series selectors.', 'example':[record['request']['match[]']]}
    request_name = schema_name.replace('Response','Request')
    request_example={k:[v] if k=='match[]' else v for k,v in record['request'].items()}
    prom['components']['schemas'][request_name]={'type':'object','required':list(record['request']),'properties':properties,'example':request_example}
    # Relative gateway URLs allow local and public Swagger to use the same YAML.
    curl=['curl --fail-with-body -sS \\', "  -u 'labreader:prometheus-lab-demo' \\",f"  'http://127.0.0.1:8085/sandbox/prometheus/api/v1/{key}' \\"]
    for n,(field,value) in enumerate(record['request'].items()):
        curl.append(f"  --data-urlencode '{field}={value}'" + (' \\' if n<len(record['request'])-1 else ''))
    source='\n'.join(curl)+'\n'
    (ROOT/'samples'/f'prometheus_{key}.sh').write_text('#!/bin/sh\n# '+title+'. Run npm start before this request.\nset -eu\n'+source)
    operation={'operationId':key,'summary':title,'tags':[tag],
        'description':f'{title} using the documented values. The replay response was captured from native Prometheus 3.5.0. '
         'POST accepts URL-encoded fields; no path parameters are needed.',
        'parameters':[], 'requestBody':{'required':True,'content':{'application/x-www-form-urlencoded':{
            'schema':ref(request_name),'example':request_example,
            **({'encoding':{'match[]':{'style':'form','explode':True}}} if 'match[]' in properties else {})}}},
        'responses':{'200':{'description':'Native capture replayed successfully.','content':{'application/json':{
            'schema':ref(schema_name),'example':record['payload']}}},**errors()},
        'x-codeSamples':[{'lang':'Shell','label':'curl local gateway','source':source}]}
    if key=='query':
        operation['responses']['400']['content']['application/json']['example']=capture('query_invalid')['payload']
    prom['paths']['/api/v1/'+key]={'post':operation}

corg = base('Corg ly Onboarding Training API',
    'UE-5 training mock. No production Corg.ly API is claimed. Photo and audio fixtures validate multipart transport only. '
    'Photos are not stored; bark meaning is deterministic; webhook deliveries are disabled. '
    'Bearer token corgly-lab-einstein-2026 is a public opaque demo token, not a JWT.', '/v1','BearerAuth')
corg['components']['securitySchemes']['BearerAuth']={'type':'http','scheme':'bearer','description':'Opaque public demo token: corgly-lab-einstein-2026. Not a production credential or JWT.'}
corg['tags']=[{'name':'Onboarding','description':'Pet media and activity subscriptions.'}]
for key,path,title,request_type,response_name in [
 ('upload_photo','/pets/upload-photo','Upload Einstein photo','multipart/form-data','PhotoResponse'),
 ('translate_bark','/audio/translate-bark','Translate Einstein bark','multipart/form-data','BarkResponse'),
 ('subscribe_webhook','/webhooks/subscribe','Subscribe to Einstein activity','application/json','WebhookResponse')]:
    record=capture(key)
    corg['components']['schemas'][response_name]={**infer(record['payload']),'example':record['payload']}
    props={'pet_id':{'type':'string','enum':['corgi_98231'],'example':'corgi_98231'}}
    if key=='upload_photo':
        props['photo']={'type':'string','format':'binary','description':'PNG or JPEG; 1 byte to 2 MiB. Included fixture: samples/assets/einstein.png.'}
        example={'pet_id':'corgi_98231','photo':'einstein.png'}
    elif key=='translate_bark':
        props.update({'audio':{'type':'string','format':'binary','description':'WAV; 1 byte to 2 MiB. Included fixture: a tone, not a real bark.'},'language':{'type':'string','enum':['en'],'example':'en'}})
        example={'pet_id':'corgi_98231','audio':'einstein_bark.wav','language':'en'}
    else:
        props.update({'callback_url':{'type':'string','format':'uri','pattern':'^https://','example':ORIGIN+'/callbacks/einstein'},
            'events':{'type':'array','minItems':1,'items':{'type':'string','enum':['pet.photo.uploaded','bark.translated']}}})
        example={'pet_id':'corgi_98231','callback_url':ORIGIN+'/callbacks/einstein','events':['pet.photo.uploaded','bark.translated']}
    req_name=response_name.replace('Response','Request')
    corg['components']['schemas'][req_name]={'type':'object','required':list(props),'properties':props,'example':example}
    response_codes={str(record['status']):{'description':'Verified mock response.','content':{'application/json':{'schema':ref(response_name),'example':record['payload']}}},**errors()}
    response_codes.pop('422')
    response_codes['500']={'description':'Unexpected service failure; documented, not fault-injected.','content':{'application/json':{'schema':ref('ErrorResponse')}}}
    response_codes.pop('503')
    if key!='subscribe_webhook':
        for code,desc in [(413,'File exceeds allowed size.'),(415,'Unsupported media type.')]:
            response_codes[str(code)]={'description':desc,'content':{'application/json':{'schema':ref('ErrorResponse')}}}
    corg['paths'][path]={'post':{'operationId':key,'summary':title,'tags':['Onboarding'],
        'description':(ROOT/'samples'/f'{key}.py').read_text().splitlines()[0].strip('"')+
        ' Run npm start, install requirements.txt and execute this sample from any directory. Full setup and included fixtures are in README.md.',
        'parameters':[], 'requestBody':{'required':True,'content':{request_type:{'schema':ref(req_name),'example':example}}},
        'responses':response_codes, 'x-codeSamples':[{'lang':'Python','label':'Complete executable Python','source':(ROOT/'samples'/f'{key}.py').read_text()}]}}
for filename,spec in [('openapi.yaml',prom),('corgly.yaml',corg)]:
    (ROOT/'docs/openapi'/filename).write_text(yaml.safe_dump(spec,sort_keys=False,allow_unicode=True,width=100))
    (ROOT/'public'/filename).write_text(yaml.safe_dump(spec,sort_keys=False,allow_unicode=True,width=100))
print('Authored two OpenAPI 3.0.3 contracts: five Prometheus paths and three Corg.ly paths.')
