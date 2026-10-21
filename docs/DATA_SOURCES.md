# Data-source inventory

| Source | Purpose | Status | Limits |
| --- | --- | --- | --- |
| SEC EDGAR submissions/company facts | US issuer filings and reported facts | Implemented connector | Public source; fair-access and User-Agent requirements; not real-time quotes |
| Configured RSS feeds | Publisher/official announcements | Implemented connector | User-configured only; publisher terms apply; coverage is not comprehensive |
| Uploaded user documents | Evidence-grounded private research | Implemented | User must have processing rights; local retention until deletion |
| Anthropic Messages API | Optional answer synthesis | Implemented optional provider | Requires key, network, paid/limited usage |
| Google Gemini API | Optional answer synthesis | Implemented optional provider | Requires API key; model availability and free quotas depend on Google AI Studio account |
| Brave Search API | Fresh web search for assistant questions | Implemented optional connector | Requires API key; plan, usage, and data-use terms apply; snippets link to original pages |
| Alpha Vantage Global Quote | Market quotes by ticker | Implemented optional connector | Requires API key; default is end-of-day; realtime/delayed US data requires premium entitlement; NSE/BSE coverage is not promised |
| RBI, SEBI, NSE RSS | Indian policy releases, regulator notices, listed-company announcements and corporate actions | Implemented through configured official RSS feeds | Public headline/feed coverage only; updates may be delayed; not a complete filing or news archive |
| NSE/BSE market data | Indian equity prices and market information | Not connected as a full exchange quote provider | Complete/redistributed live coverage requires an authorized exchange/vendor agreement. Alpha Vantage may not cover Indian symbols |
| Licensed quotes and premium financial news | Prices and paid media | Not connected | Select provider and obtain appropriate subscription/permissions |

Every displayed external item should expose its source and timestamps. Unsupported feeds are empty, not filled with mock content.
