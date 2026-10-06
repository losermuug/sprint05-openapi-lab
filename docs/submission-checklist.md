# Sprint 05 submission checklist

- Source: sandbox/, api/, scripts/, tests/, package.json and package-lock.json.
- Main OpenAPI: docs/openapi/openapi.yaml (OpenAPI 3.0.3, five Prometheus paths).
- UE-5 OpenAPI: docs/openapi/corgly.yaml and three complete Python samples in samples/.
- Report: reports/week05 lab.docx (Week 04 template, Mongolian).
- Audit: docs/audit-scorecard.md (all eight samples, 4.90/5 self-audit).
- Decision: docs/decision-report.md (100-word body).
- Public Swagger UI: https://sprint05-openapi-lab.vercel.app/swagger/
- Public Redoc: https://sprint05-openapi-lab.vercel.app/redoc/
- Corg.ly Redoc: https://sprint05-openapi-lab.vercel.app/redoc/corgly.html
- CI: .github/workflows/lab.yml runs lint, document build and all 43 sample/schema/error checks.

The public API is a training sandbox. Prometheus replies replay native captures; Corg.ly is a mock. It does not store photos, infer actual bark meanings, or send webhooks. Required literature page references currently come from the supplied lab handout; full book chapters have not been independently checked. Search works, but no separate performance benchmark has been conducted.
