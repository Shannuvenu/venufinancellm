# Security and privacy

- Local development services bind to `127.0.0.1`. Hosted frontend requests pass through the protected Next.js proxy; set `APP_PASSWORD` on the frontend and the matching server-only `APP_INTERNAL_TOKEN` on both hosts.
- `APP_ENV=production` makes the FastAPI API reject requests without the internal gateway token. `/healthz` reveals only database availability for the host health check.
- Secrets belong in `.env`, which is ignored by Git. Never add API secrets to `NEXT_PUBLIC_*`, logs, screenshots, source control, or chat.
- Treat uploaded files, RSS content, and retrieved excerpts as untrusted data. Instructions found inside a document are evidence text, never application instructions.
- Upload size and extension limits are enforced. Store only files you have rights to process. Local uploaded files and extracted text are retained in the app database/storage until deleted.
- Portfolio entry is local to the browser and is not transmitted to the backend.
- The application is research-only and has no broker-order route.
- The deployment guide is for one private owner workspace protected by shared HTTP Basic credentials. Before multi-user deployment, add individual accounts, per-user data isolation, CSRF protections, backup encryption, retention policy controls, and production-grade rate limiting.
