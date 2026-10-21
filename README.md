# VenuFin AI

VenuFin AI is a local-first financial research workspace. The first release includes a FastAPI backend, responsive research UI, deterministic financial calculators, document ingestion and retrieval, source-aware provider interfaces, and setup notes for optional services.

## Start on Windows

1. Install Python 3.11+ and Node.js 20.9+.
2. Copy `.env.example` to `.env` and fill in only the providers you intend to use.
3. In PowerShell, run `scripts\setup.ps1` once.
4. Run `scripts\start.ps1`, then open http://127.0.0.1:3000.

The app runs in limited mode without API credentials. No sample market prices or fabricated news are shown. PostgreSQL is the configured production database; SQLite is used only as a zero-setup local fallback. The optional Sentence Transformers package is kept out of the base install because it pulls in PyTorch; install it using the command shown by setup to activate local semantic embeddings. Until then, retrieval uses its labeled deterministic lexical fallback.

## Current capabilities

- Local document upload, PDF/text extraction, chunking, embedding and citation-aware retrieval. Sentence Transformers is used when installed; the local fallback is lexical and is explicitly labeled.
- Google Gemini and Anthropic provider adapters for answer generation; without a key, source results are still shown without synthesis.
- Deterministic calculator endpoints and a browser calculator for CAGR/returns, loans/SIP, valuations, cash flows, FX conversions, options/futures payoffs, and portfolio risk metrics.
- Source-aware SEC submissions/company facts connectors, configured public RSS ingestion, and clear provider health states.
- Optional live Brave web search with linked sources and Alpha Vantage ticker quotes that label the actual data entitlement and trading date.
- Local portfolio analysis from user-entered data; nothing is sent to a provider.
- Windows setup and start scripts, provider/source inventory, security notes, API docs, and tests.

See [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md), [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md), and [docs/FINAL_SETUP.md](docs/FINAL_SETUP.md).

## API

FastAPI is served at http://127.0.0.1:8000. Interactive endpoint documentation is at `/docs`; `/api/health` reports connected capabilities. The backend binds to loopback by default.

## Safety

This is a research and learning tool, not investment advice or a broker. It does not place orders or enable live trading. Current-data answers require retrieved sources; calculators report assumptions and do not invent missing inputs. Keep `.env` private and use only data sources whose access terms permit your use.
