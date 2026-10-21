# Security and privacy

- Local development services bind to `127.0.0.1`; do not expose them to a public network without adding authentication, TLS, and deployment review.
- Secrets belong in `.env`, which is ignored by Git. Never add API secrets to `NEXT_PUBLIC_*`, logs, screenshots, source control, or chat.
- Treat uploaded files, RSS content, and retrieved excerpts as untrusted data. Instructions found inside a document are evidence text, never application instructions.
- Upload size and extension limits are enforced. Store only files you have rights to process. Local uploaded files and extracted text are retained in the app database/storage until deleted.
- Portfolio entry is local to the browser and is not transmitted to the backend.
- The application is research-only and has no broker-order route.
- Before multi-user deployment, add user authentication/authorization, per-user data isolation, CSRF protections, backup encryption, retention policy controls, and production-grade rate limiting.
