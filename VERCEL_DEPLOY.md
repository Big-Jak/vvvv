# Deploying to Vercel

Unlike Render, Vercel runs Django as serverless functions with no persistent
local disk — so file uploads (student PDFs) can't be written to `MEDIA_ROOT`
like they can on a normal server. This app is now set up to detect that and
switch to S3-compatible object storage automatically when the right
environment variables are present. If they're absent, it falls back to local
disk exactly as before (so this same codebase still works unchanged on
Render or your own machine).

## 1. Push to GitHub
Same as before — `.env` stays out of the repo (already gitignored).

## 2. Set up a database
Vercel doesn't host Postgres itself. Use a provider like **Neon** or
**Supabase** (both have generous free tiers and a one-click Vercel
integration in the Vercel dashboard's Storage tab), or add Vercel's own
Postgres integration if available on your plan. Either way you'll end up
with a `DATABASE_URL` connection string.

## 3. Set up object storage for uploads
Any S3-compatible provider works. **Cloudflare R2** is a good default (free
tier, no egress fees). Create a bucket and an access key, then note:
- Bucket name
- Access key ID / secret access key
- Endpoint URL (R2 gives you one like `https://<account-id>.r2.cloudflarestorage.com`)
- Region (R2 doesn't use real regions — `auto` works)

## 4. Import the project into Vercel
Vercel dashboard → Add New → Project → import your GitHub repo. It
auto-detects Django from `manage.py` and `requirements.txt` — no framework
selection needed.

## 5. Environment variables
Set these in the Vercel project's Settings → Environment Variables:

| Key | Value |
|---|---|
| `SECRET_KEY` | generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `false` |
| `DATABASE_URL` | connection string from step 2 |
| `AWS_STORAGE_BUCKET_NAME` | your bucket name from step 3 |
| `AWS_ACCESS_KEY_ID` | from step 3 |
| `AWS_SECRET_ACCESS_KEY` | from step 3 |
| `AWS_S3_ENDPOINT_URL` | your bucket's endpoint URL (leave unset for real AWS S3) |
| `AWS_S3_REGION_NAME` | `auto` for R2, or your real AWS region |
| `ANTHROPIC_API_KEY` | optional — without it, essays get fallback scoring |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_USE_TLS` | optional |

You don't need to set `ALLOWED_HOSTS` — the app detects it's running on
Vercel (via the `VERCEL` and `VERCEL_URL` variables Vercel sets
automatically) and trusts your `*.vercel.app` domain, including preview
deployments, on its own. If you add a custom domain, add it to
`ALLOWED_HOSTS` explicitly.

## 6. Deploy
Vercel builds automatically on push. `vercel.json` in this repo tells it to
run migrations during the build (`python manage.py migrate`); static files
are collected automatically — you don't need to configure that part.

## Notes / limitations
- **Cold starts**: serverless functions spin down between requests on low
  traffic, so the first request after idle time will be slower.
- **Function timeout**: `vercel.json` sets a 60-second limit for AI feedback
  requests, which needs a paid Vercel plan (Hobby is capped at 10 seconds —
  may not be enough for slower AI responses or large PDF uploads).
- **No background workers**: this app doesn't currently have any, but if you
  add scheduled jobs later, they'd need Vercel Cron or an external worker,
  not a long-running process.
