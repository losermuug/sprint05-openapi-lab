"""Submit the included WAV fixture; the mock returns a fixed bark meaning."""
import json
import os
from pathlib import Path
import requests

base_url = os.getenv('CORGLY_BASE_URL', 'http://127.0.0.1:8085').rstrip('/')
auth_token = os.getenv('CORGLY_TOKEN', 'corgly-lab-einstein-2026')
audio_path = Path(__file__).parent / 'assets' / 'einstein_bark.wav'
with audio_path.open('rb') as audio_file:
    bark_response = requests.post(
        f'{base_url}/v1/audio/translate-bark',
        headers={'Authorization': f'Bearer {auth_token}'},
        data={'pet_id': 'corgi_98231', 'language': 'en'},
        files={'audio': (audio_path.name, audio_file, 'audio/wav')},
        timeout=10,
    )
bark_response.raise_for_status()
assert bark_response.status_code == 200
print(json.dumps(bark_response.json(), indent=2))
