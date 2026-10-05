# Sprint 05 OpenAPI 3.0 ба Bhatti кодын жишээ

Week 04 тайлангийн Prometheus төслийг үргэлжлүүлсэн лабораторийн багц. Үндсэн API нь Prometheus-ийн таван native POST интерфэйс; заавал хийх UE-5 нь Corg.ly mock API-ийн гурван Python жишээ.

## Ажиллуулах

Node 22+ болон Python 3.12 ашиглана. Энэ хавтсыг terminal-д нээгээд:

```sh
npm ci
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
npm run lint
npm run build:docs
npm start
```

Дараа нь http://127.0.0.1:8085/swagger/ болон http://127.0.0.1:8085/redoc/ хаягаар үзнэ. Хоёр дахь terminal-д:

```sh
. .venv/bin/activate
python tests/verify_lab.py
python samples/upload_photo.py
python samples/translate_bark.py
python samples/subscribe_webhook.py
sh samples/prometheus_query.sh
```

Python жишээнүүдийг ямар ч working directory-оос ажиллуулж болно: fixture замыг `__file__`-ээс олно. Curl жишээнүүд нь зориуд локал gateway хаягтай. Нийтийн API-г шалгахдаа `LAB_BASE_URL` болон `CORGLY_BASE_URL`-ийг deployment-ийн origin-оор тохируулна.

## Authentication

Prometheus gateway нь HTTP Basic: `labreader` / `prometheus-lab-demo`. Corg.ly нь opaque Bearer token: `corgly-lab-einstein-2026`. Эдгээр нь зөвхөн нийтэд харагдах сургалтын demo утгууд. Swagger UI-ийн Authorize цонхонд оруулна. Corg.ly тодорхойлолтыг Select a definition хэсгээс сонгоно.

## Хамрах хүрээ

`docs/openapi/openapi.yaml` нь OpenAPI 3.0.3, 5 distinct paths, бүх operation-д form requestBody, request ба response examples, shared schemas, 200/400/401/422/503 response codes агуулна. `parameters: []` нь эдгээр POST интерфэйсэд path/query parameter байхгүйг илэрхийлнэ; бүх input requestBody-д байна. Native Prometheus-ийн бүрэн API-ийн хувилбар биш: sample corpus-ийн vector, matrix, metadata ба formatting хэлбэрийг баримтжуулсан.

Native Prometheus 3.5.0 нь 127.0.0.1:9095 дээр ажиллаж, query, query_range, series, labels, format_query болон parse error хариуг авсан. Баригдсан JSON нь docs/evidence-д source, request, status-тай хадгалагдсан. Нийтийн gateway эдгээрийг replay хийдэг; өөр PromQL, timestamp эсвэл selector илгээвэл 422. BasicAuth нь лабораторийн gateway-д хамаарна; native capture сервер loopback дээр auth-гүй байсан.

Corg.ly бол lab mock. Файлыг хадгалахгүй, bark-ийн утга тогтмол, webhook delivery хийхгүй. PNG нь 16 x 16 нэг өнгийн transport fixture; WAV нь 440 Hz tone. Production Corg.ly API, бодит амьтны дуу таних систем гэж тайлбарлаагүй. 500/503 response codes баримтжуулсан боловч fault injection хийгдээгүй.

## Багцын бүтэц

- docs/openapi/ — хоёр YAML contract
- docs/evidence/ — native болон mock хариу, автомат шалгалтын дүн
- docs/audit-scorecard.md — бүх 8 жишээний Bhatti аудит, 4.90/5 буюу 98%
- docs/decision-report.md — яг 100 үгтэй renderer сонголт
- samples/ — 5 curl ба 3 бүрэн Python жишээ, fixture файлууд
- sandbox/ — локал ба public Worker-ийн shared API handler
- public/ — Swagger UI, Redoc, YAML болон унших баримт
- tests/verify_lab.py — executable samples, schema ба сөрөг хувилбарууд
- .github/workflows/lab.yml — яг энэ шалгалтыг push/PR үед гүйцэтгэх CI

## Нийтийн байршуулалт

Swagger UI: https://swpd-sprint05-openapi-lab.ganzorigm04.chatgpt.site/swagger/

Redoc: https://swpd-sprint05-openapi-lab.ganzorigm04.chatgpt.site/redoc/

Corg.ly Redoc: https://swpd-sprint05-openapi-lab.ganzorigm04.chatgpt.site/redoc/corgly.html

Deployment-ийн баталгаажсан мэдээллийг docs/evidence/deployment.json-д хадгална. Sites source repository-д source commit хадгалагдана. GitHub Actions workflow-ийн эх код бэлэн; GitHub дээр run хийсэн гэж батлаагүй. CI-ийн ижил командыг локал орчинд ажиллуулсан.

## Эх сурвалж

Sprint 05 Lab Instructions — US-5.1–5.4, UE-5, DoD, Bhatti Ch.5 pp.83–99 ба Ch.7 pp.121–130, Chinchilla Ch.2 pp.18–22 ба Ch.6 p.79 гэсэн унших чиглэл.

Prometheus HTTP API: https://prometheus.io/docs/prometheus/latest/querying/api/

Redocly CLI lint: https://redocly.com/docs/cli/commands/lint

Redoc Community: https://redocly.com/docs/redoc

Номын хуудсын заалтыг багшийн PDF-д өгсөн лавлагаагаар ашигласан; номын бүтэн эхийг энэ багцад оруулаагүй.
