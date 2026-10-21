# Private deployment guide

VenuFin is a single-workspace financial research app. The deployment below protects the site with one shared username and password and keeps the API behind a server-to-server token. It is for a private owner preview; it does not provide separate user accounts or per-user document isolation.

## Before deploying

1. Rotate any provider keys previously pasted into chat or screenshots. Put replacements only in the backend host's secret settings.
2. Push the current project version to GitHub.
3. Generate a strong `APP_PASSWORD` and a separate random `APP_INTERNAL_TOKEN`. Set the same internal token on both services. Never commit these values or put them in a `NEXT_PUBLIC_*` variable.
4. Choose data providers. The included RBI, SEBI, and NSE RSS feeds are public announcements, not comprehensive financial news. Alpha Vantage does not promise complete NSE/BSE coverage. Use an authorized licensed vendor or exchange agreement for comprehensive or commercial market data.

## Deploy both services on Render

Use two Render Web Services in the same region: a Docker API service and a Node.js Next.js service. This deployment keeps 25 MB document uploads on the Node server path and avoids Vercel Functions' 4.5 MB request-body limit.

### 1. Create PostgreSQL

In Render, create a PostgreSQL database. Keep it in the same region as the services. Copy its **Internal Database URL**. Before using it, make sure the scheme is `postgresql+psycopg://` (the Python API uses psycopg 3); preserve the username, password, host, port, and database name.

### 2. Create the API service

Create a Web Service from `Shannuvenu/venufinancellm`, choose **Docker**, and leave the Root Directory blank so the root [Dockerfile](../Dockerfile) is used. Set the health check path to `/healthz`. Attach a persistent disk mounted at `/var/data`; without it, uploaded originals disappear on redeploy. Render persistent disks require a paid service plan.

Add these environment variables in the API service settings:

| Variable | Value |
| --- | --- |
| `APP_ENV` | `production` |
| `APP_INTERNAL_TOKEN` | The generated private token |
| `DATABASE_URL` | The internal PostgreSQL URL using `postgresql+psycopg://` |
| `UPLOADS_DIR` | `/var/data/uploads` |
| `NEWS_RSS_URLS` | The comma-separated RBI, SEBI, NSE, and other feed URLs from `.env.example` |
| `GEMINI_API_KEY` | Optional; rotated Gemini key |
| `ALPHAVANTAGE_API_KEY` | Optional; rotated Alpha Vantage key |
| `BRAVE_SEARCH_API_KEY` | Optional; if configured |
| `SEC_USER_AGENT` | `VenuFinAI contact: your-monitored-email@example.com` |

After deployment, copy the API service's public HTTPS URL. Direct `/api/*` requests require the internal token; `/healthz` is public for service health checks.

### 3. Create the website service

Create another Web Service from the same GitHub repository and choose **Node**. Set **Root Directory** to `frontend`, **Build Command** to `npm ci && npm run build`, and **Start Command** to `npm start`.

Add these environment variables:

| Variable | Value |
| --- | --- |
| `BACKEND_URL` | The API HTTPS URL, without a trailing slash |
| `APP_INTERNAL_TOKEN` | The same private token configured on the API |
| `APP_USERNAME` | Your login name (defaults to `owner`) |
| `APP_PASSWORD` | Your strong private password |

The browser talks to the website service on the same origin. The Next.js proxy forwards API traffic and adds the server-side token. The middleware prompts for HTTP Basic Auth credentials. Do not put provider credentials in the website service.

## Verify

1. Open the website service URL and sign in.
2. Check the app's source and provider status panels.
3. Ask it to summarize a recent RBI or SEBI announcement. Confirm that it shows the source link and publication date.
4. In Document Lab, upload a few PDFs together and confirm the indexed, duplicate, or failed counts.
5. Check the source and date for any quote. A working quote for one symbol does not prove full NSE/BSE coverage.

## Coverage and operating limits

- Default official feeds cover selected RBI releases, SEBI RSS items, and NSE announcements/corporate actions; they do not contain every Indian company filing or news publisher.
- The stock connector is Alpha Vantage Global Quote. It may not return Indian symbols and is not an all-NSE/all-BSE market feed.
- VenuFin retrieves uploaded documents as context; uploads do not retrain the underlying model. The `INDIA_100_DOCUMENT_STARTER_PACK.md` is a source checklist for building a reference library, not 100 bundled reports.
- For multi-user production, add account authentication, user-level data isolation, backup/restore, and retention controls before inviting users.

## Official deployment references

- [Render: deploy a Next.js app](https://render.com/docs/deploy-nextjs-app)
- [Render: web services](https://render.com/docs/web-services)
- [Render: PostgreSQL](https://render.com/docs/databases)
- [Render: persistent disks](https://render.com/docs/disks)
- [Vercel: function limitations](https://vercel.com/docs/functions/limitations) (documents the 4.5 MB body limit if you choose Vercel instead)
