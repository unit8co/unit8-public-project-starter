# Environment Variables

The application reads settings from `.env` and optional overrides from
`.env.local`.

## Core runtime

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_NAME` | `agentic-project-starter` | Service name used in API metadata and logs |
| `APP_ENVIRONMENT` | `local` | Runtime profile such as `local`, `docker`, or `ci` |
| `APP_HOST` | `0.0.0.0` | Bind host for local and container execution |
| `APP_PORT` | `8000` | Bind port for local and container execution |
| `LOG_LEVEL` | `INFO` | Root log level |

## OpenAI and agentic settings

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | empty | API key required for live OpenAI calls |
| `OPENAI_MODEL` | `gpt-5` | Default model name used by starter agent definitions |
| `OPENAI_DEFAULT_AGENT` | `coordinator` | Default agent name for project-specific wrappers |
| `OPENAI_ENABLE_TRACING` | `false` | Flag reserved for future tracing integration |
| `CHATKIT_DOMAIN_KEY` | `local-dev` | Domain key passed to the optional self-hosted ChatKit frontend |

## Data and observability

| Variable | Default | Purpose |
| --- | --- | --- |
| `STORAGE_URI` | `file://./var/data` | Starter storage location for local or containerized work |
| `ETL_DEFAULT_DATASET` | `demo-dataset` | Default dataset identifier for CLI ETL commands |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | empty | Optional OTLP endpoint for telemetry export |

## Files

- `.env.example`: committed template
- `.env`: local developer secrets and overrides
- `.env.local`: optional higher-priority local overrides
- `.env.docker.example`: example container-oriented overrides
- `frontend/.env.example`: frontend development example values for the optional ChatKit accelerator
- `frontend/.env.local`: local frontend overrides such as `VITE_API_BASE_URL`
