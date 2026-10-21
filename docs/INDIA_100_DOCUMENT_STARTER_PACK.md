# VenuFin India: 100-document starter pack

This is a practical first corpus for Indian listed-company research. It is **not** a claim to cover every Indian financial fact or every listed company. The company set is the current Nifty 50, which is a focused starting universe and must be refreshed when the index changes.

## The 100 company documents

For each of the 50 companies in the current Nifty 50, download these two documents from the exchange's company filing page:

1. The latest available **annual report** (audited, with notes and auditor's report).
2. The latest available **quarterly financial results** (consolidated where available; include the exchange filing date).

That is 50 × 2 = **100 issuer documents**. Get the current constituent CSV from the [official Nifty 50 index page](https://www.nseindia.com/static/products-services/indices-nifty50-index). Do not use an old constituent list copied into this guide.

Find reports through the [NSE corporate filings portal](https://www.nseindia.com/companies-listing/corporate-filings) or [BSE company filings](https://www.bseindia.com/corporates.html). Confirm the company name and NSE/BSE symbol before saving each report. Prefer the original exchange-hosted filing or issuer investor-relations source. Do not use third-party scraped copies if the official filing is available.

Suggested filenames:

```text
annual_<NSE_SYMBOL>_<FY>.pdf
quarterly_<NSE_SYMBOL>_<period>_<filing-date>.pdf
```

Keep one company per file, preserve the original PDF, and record the source URL and publication date. In VenuFin's Document Lab, select or drop multiple PDFs; they upload sequentially with indexed, duplicate, and failed counts. The limit is 25 MB per file. Scanned/image-only PDFs may not yield searchable text.

## Ten useful reference documents to add after the company reports

These are official source collections; choose the latest edition and the relevant report or chapter:

1. [RBI Annual Report](https://www.rbi.org.in/Scripts/AnnualReportPublications.aspx)
2. [RBI Report on Trend and Progress of Banking in India](https://www.rbi.org.in/Scripts/AnnualPublications.aspx?head=Trend%20and%20Progress%20of%20Banking%20in%20India)
3. [RBI Financial Stability Report archive](https://www.rbi.org.in/Scripts/FsReports.aspx)
4. [RBI Handbook of Statistics on the Indian Economy](https://www.rbi.org.in/Scripts/AnnualPublications.aspx?head=Handbook%20of%20Statistics%20on%20Indian%20Economy)
5. [RBI Bulletin](https://bulletin.rbi.org.in/)
6. [SEBI Annual Reports](https://www.sebi.gov.in/reports-and-statistics/publications.html)
7. [SEBI reports and statistics](https://www.sebi.gov.in/reports.html) — use the latest Handbook of Statistics / Bulletin available there.
8. [Economic Survey of India](https://www.indiabudget.gov.in/economicsurvey/)
9. [Union Budget documents](https://www.indiabudget.gov.in/)
10. [NSE company announcements and filings](https://www.nseindia.com/companies-listing/corporate-filings-announcements)

The reference list is additive: 100 company documents plus these references gives at least 110 files. Replace older editions when new ones are published; keep the publication date in the filename or metadata.

## To cover all Indian stocks and daily facts

Static documents build searchable background. They do not update prices, news, or filings by themselves. India has thousands of listed companies, so extend beyond Nifty 50 using the full NSE/BSE listed-company universe and ingest new exchange filings on a schedule.

- For an experimental, informational integration, NSE publishes [MCP market-data servers](https://www.nseindia.com/nse-mcp): the Bhavcopy tools provide up to five years of end-of-day history, and CM Market Live is described as roughly 1–3 minutes delayed. NSE's page explicitly restricts use to informational/non-commercial purposes and says access does not grant commercial exploitation or AI-training rights. Read its current terms before connecting it.
- For a commercial or broadly distributed service, contact [NSE Data & Analytics](https://www.nseindia.com/static/nse-data-and-analytics) and [BSE Market Data](https://marketdata.bseindia.com/) for authorized feeds, coverage, latency, and licensing. Do not present a free or delayed source as exchange-authorized real-time data.
- Keep daily news and corporate announcements in a refreshable feed/API, with source URL, timestamp, and freshness shown in answers. Uploads are for documents; live-data providers are for changing facts.

## Daily upkeep

1. Refresh the Nifty 50 constituents list whenever NSE Indices changes it.
2. Check exchange filings daily for results, corporate actions, shareholding patterns, and material announcements.
3. Replace old quarter reports after the next results are filed; retain annual reports for history.
4. Refresh RBI, SEBI, Budget, and Economic Survey references when newer editions appear.
5. Ask VenuFin to cite the filing/report and date. Treat uploaded files as evidence to retrieve, not as model training: the app indexes documents for search and does not make the underlying model learn permanently.

## Current VenuFin limits

The Document Lab accepts PDF, TXT, Markdown, HTML, CSV, and TSV (25 MB max per file) and extracts searchable text locally. Select a batch of files to index a 100-file corpus. The live market coverage depends on connected providers, not on these reports. Alpha Vantage configured in this project is not a substitute for a licensed full NSE/BSE feed.
