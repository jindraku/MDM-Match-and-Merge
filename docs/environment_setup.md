# Environment Setup

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make test
make profile
make run
```

## Environment variables

`.env.example` includes:
- dataset path and output paths
- Groq model, feature flags, and API key placeholders
- Azure Maps API key placeholders

## Provisioned assets included in this repository

- Local Python runtime definition via `requirements.txt`
- Reproducible run targets via `Makefile`
- Container starter via `Dockerfile`
- CI workflow via `.github/workflows/ci.yml`
- Integration-ready provider configuration via `.env.example`

## Expected enterprise follow-up outside the repo

- store API keys in CI secret manager
- provision service accounts or key rotation policy
- create separate dev, test, and prod environment variables
- connect the input path to the real MDM source instead of CSV
