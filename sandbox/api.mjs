// Training API. Prometheus replies replay native 3.5.0 captures; Corg.ly is a mock.
export const DEMO_BEARER = 'corgly-lab-einstein-2026';
const basic = 'Basic ' + btoa('labreader:prometheus-lab-demo');
const json = (payload, status = 200, headers = {}) => new Response(JSON.stringify(payload), {
  status, headers: { 'Content-Type': 'application/json', 'X-Lab-Mode': 'training-sandbox', ...headers }
});
const failure = (message, status = 400, type = 'bad_data', headers = {}) =>
  json({status: 'error', errorType: type, error: message}, status, headers);

export async function handleApi(request, evidence) {
  const url = new URL(request.url);
  const path = url.pathname;
  if (path === '/health') return json({status: 'ready', mode: 'training-sandbox'});
  if (!path.startsWith('/sandbox/') && !path.startsWith('/v1/')) return null;
  if (request.method !== 'POST') return failure('Use POST for this endpoint.', 405, 'bad_data', {Allow:'POST'});
  if (path.startsWith('/sandbox/prometheus/')) {
    if (request.headers.get('Authorization') !== basic)
      return failure('Valid laboratory Basic credentials are required.', 401, 'unauthorized', {'WWW-Authenticate':'Basic realm="SWPD laboratory"'});
    const key = path.split('/').at(-1);
    if (!evidence[key]) return failure('Endpoint not found.', 404);
    const params = await request.formData();
    const expected = evidence[key].request;
    if (key === 'query' && params.get('query') === 'sum(')
      return json(evidence.query_invalid.payload, 400);
    if (!Object.entries(expected).every(([name, value]) => params.get(name) === value))
      return failure('This replay sandbox supports only the documented example inputs.', 422, 'unsupported_sample');
    return json(evidence[key].payload, evidence[key].status);
  }
  if (request.headers.get('Authorization') !== `Bearer ${DEMO_BEARER}`)
    return failure('The laboratory bearer token is required.', 401, 'unauthorized', {'WWW-Authenticate':'Bearer'});
  if (Number(request.headers.get('Content-Length') || 0) > 2 * 1024 * 1024)
    return failure('Maximum upload size is 2 MiB.', 413);
  try {
    if (path === '/v1/pets/upload-photo') {
      const form = await request.formData();
      const photo = form.get('photo');
      if (form.get('pet_id') !== 'corgi_98231' || !photo || typeof photo === 'string')
        return failure('pet_id corgi_98231 and a photo file are required.');
      if (!['image/png', 'image/jpeg'].includes(photo.type)) return failure('Use PNG or JPEG.', 415);
      if (!photo.size || photo.size > 2 * 1024 * 1024) return failure('Photo must contain 1 byte to 2 MiB.', 413);
      return json({pet_id: 'corgi_98231', pet_name: 'Einstein', photo_id: 'photo_einstein_001',
        filename: photo.name, content_type: photo.type, size_bytes: photo.size, stored: false, mode: 'mock'}, 201);
    }
    if (path === '/v1/audio/translate-bark') {
      const form = await request.formData();
      const audio = form.get('audio');
      if (form.get('pet_id') !== 'corgi_98231' || form.get('language') !== 'en' || !audio || typeof audio === 'string')
        return failure('pet_id corgi_98231, language en and an audio file are required.');
      if (audio.type !== 'audio/wav') return failure('Use a WAV file.', 415);
      if (!audio.size || audio.size > 2 * 1024 * 1024) return failure('Audio must contain 1 byte to 2 MiB.', 413);
      const bytes = new Uint8Array(await audio.arrayBuffer());
      if (new TextDecoder().decode(bytes.slice(0,4)) !== 'RIFF' || new TextDecoder().decode(bytes.slice(8,12)) !== 'WAVE')
        return failure('Invalid WAV header.');
      return json({pet_id: 'corgi_98231', translation_id: 'bark_einstein_001', meaning: 'I want to play',
        language: 'en', confidence: 0.93, mode: 'mock', model: 'deterministic-lab-fixture'});
    }
    if (path === '/v1/webhooks/subscribe') {
      const payload = await request.json();
      let callback;
      try { callback = new URL(payload.callback_url); } catch { return failure('An absolute HTTPS callback_url is required.'); }
      if (callback.protocol !== 'https:' || payload.pet_id !== 'corgi_98231' ||
          !Array.isArray(payload.events) || !payload.events.length ||
          !payload.events.every(event => ['pet.photo.uploaded', 'bark.translated'].includes(event)))
        return failure('Use HTTPS, pet_id corgi_98231 and supported pet activity events.');
      return json({subscription_id: 'hook_einstein_001', pet_id: payload.pet_id,
        callback_url: payload.callback_url, events: payload.events, status: 'active', delivery_enabled: false, mode: 'mock'}, 201);
    }
    return failure('Endpoint not found.', 404);
  } catch {
    return failure('The request body cannot be parsed.');
  }
}
