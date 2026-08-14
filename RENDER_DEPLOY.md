# Deploying to Render

## 1. Push to GitHub
Make sure `.env` is NOT committed (it's already in `.gitignore`). Only `.env.example` should be tracked.

## 2. Create a Postgres database
Render dashboard → New → PostgreSQL. Once created, copy the **Internal Database URL**.

## 3. Create a Web Service
Render dashboard → New → Web Service → connect your GitHub repo.

**Build Command:**
```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

**Start Command:**
```
gunicorn project.wsgi:application
```

## 4. Environment variables
Set these on the Web Service (Environment tab):

| Key | Value |
|---|---|
| `SECRET_KEY` | generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `false` |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` |
| `DATABASE_URL` | the Internal Database URL from step 2 |
| `ANTHROPIC_API_KEY` | optional — without it, essays get fallback scoring instead of real AI feedback |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_USE_TLS` | optional — without these, emails are skipped with a warning instead of failing |

## 5. Deploy
Render builds and runs migrations automatically via the build command. Once it's live, just sign up through the site — no `createsuperuser` needed unless you also want Django admin access.

## Notes
- Render's free Postgres expires after 30 days — fine for testing, not for going live. The Starter web service + Basic Postgres plan (~$13/mo) removes that limit along with the free tier's cold starts.
- Uploaded PDFs are stored on local disk (`MEDIA_ROOT`), which is wiped on every redeploy on Render's web service. Attach a persistent Disk mounted at `/media`, or move to S3/Cloudinary, if you need uploads to survive deploys.
