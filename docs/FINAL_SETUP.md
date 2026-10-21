# FINAL SETUP — CONNECT YOUR FINANCIAL DATA AND LLM PROVIDERS

The app is useful in limited mode without credentials. Configure these locally in `D:\VenuFinAI\.env`; do not send secrets in chat.

## Anthropic (optional reasoning)

- Official service: [Anthropic Console](https://console.anthropic.com/) and [API documentation](https://docs.anthropic.com/en/api/messages).
- Needed for generated synthesis and conversational document answers. Document extraction/search and deterministic calculators remain available without it.
- API use is paid/usage-metered and subject to account limits.
- Set `ANTHROPIC_API_KEY` and, if desired, `ANTHROPIC_MODEL` in `.env`. The default is `claude-sonnet-5`; confirm it is enabled for your account and check Anthropic's live [model status](https://docs.anthropic.com/en/docs/about-claude/model-deprecations) before changing it.
- Verify via `/api/health`, then send a non-sensitive assistant question. Secret values are never returned by health checks.

## Google Gemini (optional reasoning)

- Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/app/apikey).
- Add `GEMINI_API_KEY=your_key` to the local `.env`; `GEMINI_MODEL` defaults to `gemini-3.6-flash`.
- When both Gemini and Anthropic keys are present, Gemini is selected. Free-tier quotas and account data terms apply; review Google's current [pricing](https://ai.google.dev/gemini-api/docs/pricing) before sending private material.

## Live web research

- Create a Brave Search API key from the [Brave Search API dashboard](https://api-dashboard.search.brave.com/).
- Add `BRAVE_SEARCH_API_KEY=your_key` to the local `.env` file. The key stays on the backend and is not exposed to the browser.
- Restart VenuFin. Ask a question in AI assistant; the answer will include source links and search snippets. Without Anthropic configured, results are shown directly without AI synthesis.
- Brave's current API plans and usage terms are listed on its [official API page](https://brave.com/search/api/). Plan limits and data-use rights apply.

## Market quotes

- Create an [Alpha Vantage API key](https://www.alphavantage.co/support/#api-key) and add `ALPHAVANTAGE_API_KEY=your_key` to `.env`.
- The Markets page accepts a ticker symbol and shows its latest trading day, provider, and retrieval time.
- Alpha Vantage's default quote is end-of-day. Realtime or 15-minute delayed US quotes require a matching premium entitlement; if licensed, set `MARKET_DATA_ENTITLEMENT=realtime` or `delayed`. Check the provider's [official quote documentation](https://www.alphavantage.co/documentation/) and terms before using exchange data. This connector is not a promise of NSE/BSE coverage.
- Restart VenuFin after editing `.env`. Never put provider keys in frontend environment variables or paste them into chat.

## PostgreSQL (recommended for durable multi-user use)

- Official site: [PostgreSQL downloads](https://www.postgresql.org/download/windows/).
- Needed for a durable shared application database. Local fallback uses SQLite.
- PostgreSQL is open source. Hosting and backups may have separate costs.
- Create a database and set `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE` in `.env`. URL-escape special characters in the password.
- Restart and verify `/api/health` reports the database available.

For the private hosted setup, configure `APP_ENV=production`, `APP_INTERNAL_TOKEN`, `APP_USERNAME`, and `APP_PASSWORD` as described in [DEPLOYMENT.md](DEPLOYMENT.md). Keep the token and password in the hosting providers' secret settings only.

## SEC EDGAR (public filings)

- Official information: [SEC EDGAR APIs](https://www.sec.gov/edgar/sec-api-documentation).
- Public company submissions and company facts are useful for US filings and reported financial facts. SEC fair-access rules apply; this is not live stock pricing.
- No API key is normally required. Set `SEC_USER_AGENT` to identify the application and include a monitored contact address. Use conservative request rates and review SEC's current access guidance.
- Verify by searching a public company from the Company Research screen. Availability depends on network access and SEC service conditions.

## RSS / official news feeds (optional)

- Feed URLs and access terms vary by publisher; do not configure paid/paywalled feeds without authorization.
- Set `NEWS_RSS_URLS` to comma-separated permitted RSS feed URLs. The backend stores source URL, publisher, publication time and retrieval time where available.
- The sample `.env.example` includes free official feeds for RBI press releases and notifications, SEBI releases/circulars/orders, and NSE announcements and corporate actions, plus selected global macro feeds. These provide primary-source updates, not broad coverage of every listed company or publisher.
- The backend refreshes configured feeds every 15 minutes while running. Recent relevant items are included as assistant evidence for current-news questions, with links and publication dates.
- Verify by opening the News screen and refreshing. Only configured feeds appear.

## Other provider keys

`FRED_API_KEY`, `MARKET_DATA_API_KEY`, and `NEWS_API_KEY` are reserved configuration names and do not activate other providers. Licensed premium headlines and NSE/BSE trading data remain unavailable until a suitable provider with appropriate permissions is selected and implemented.

## Local model

Sentence Transformers downloads `sentence-transformers/all-MiniLM-L6-v2` on first use and runs embeddings locally. The model is open source; check its license and your organization’s policies. Set `EMBEDDINGS_ENABLED=false` to use the labeled lexical fallback. No embedding service credential is required.

## India Quant

No connection is active. The future interface should be read-only and schema-validated (historical observations, signals, backtest reports, fills and exposure). It must never place trades, alter risk limits, or enable live trading. Add an authorized local API only after reviewing that system’s contract and access controls.
