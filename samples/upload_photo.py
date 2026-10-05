"""Upload Einstein's included PNG to the training API; no production storage."""
import json
import os
from pathlib import Path
import requests

base_url = os.getenv('CORGLY_BASE_URL', 'http://127.0.0.1:8085').rstrip('/')
auth_token = os.getenv('CORGLY_TOKEN', 'corgly-lab-einstein-2026')
photo_path = Path(__file__).parent / 'assets' / 'einstein.png'
with photo_path.open('rb') as photo_file:
    photo_response = requests.post(
        f'{base_url}/v1/pets/upload-photo',
        headers={'Authorization': f'Bearer {auth_token}'},
        data={'pet_id': 'corgi_98231'},
        files={'photo': (photo_path.name, photo_file, 'image/png')},
        timeout=10,
    )
photo_response.raise_for_status()
assert photo_response.status_code == 201
print(json.dumps(photo_response.json(), indent=2))
