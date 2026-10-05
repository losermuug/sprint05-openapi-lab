"""Register the lab callback; the mock does not send webhook deliveries."""
import json
import os
import requests

base_url = os.getenv('CORGLY_BASE_URL', 'http://127.0.0.1:8085').rstrip('/')
auth_token = os.getenv('CORGLY_TOKEN', 'corgly-lab-einstein-2026')
callback_url = os.getenv(
    'CORGLY_CALLBACK_URL',
    'https://swpd-sprint05-openapi-lab.wiry-cup-6698.chatgpt.site/callbacks/einstein',
)
webhook_payload = {
    'pet_id': 'corgi_98231',
    'callback_url': callback_url,
    'events': ['pet.photo.uploaded', 'bark.translated'],
}
webhook_response = requests.post(
    f'{base_url}/v1/webhooks/subscribe',
    headers={'Authorization': f'Bearer {auth_token}'},
    json=webhook_payload,
    timeout=10,
)
webhook_response.raise_for_status()
assert webhook_response.status_code == 201
print(json.dumps(webhook_response.json(), indent=2))
