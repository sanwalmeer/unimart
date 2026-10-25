# UniMart

UniMart is a Django and PostgreSQL student marketplace for physical products in Islamabad. The Django app serves the frontend, API, and admin site from one domain.

## Local development

From the repository root in PowerShell:

```powershell
& .\.venv\Scripts\python.exe .\backend\manage.py migrate
& .\.venv\Scripts\python.exe .\backend\manage.py seed_unimart
& .\.venv\Scripts\python.exe .\backend\manage.py runserver 127.0.0.1:8000
```

Open `http://127.0.0.1:8000/`. Local demo mode skips email verification and provides sample catalog items when a category has no real approved listings. Sample items are never stored in the database and are disabled when `DEBUG=False`.

## Deploy to Vercel

Vercel runs Django as a Python Function. PostgreSQL must be hosted separately; `localhost` refers to the Vercel function itself, not your computer. Create a managed PostgreSQL database with a provider such as Neon, Supabase, or another PostgreSQL host, and copy its SSL-enabled connection URL.

1. Push this repository to a private or public GitHub repository. Confirm `.env` and `.env.local` are not committed.
2. In Vercel, choose **Add New Project**, import the repository, and keep the **Root Directory** set to the repository root.
3. Add these Environment Variables for **Production** (and Preview if you want preview deployments):

   - `DJANGO_SECRET_KEY`: generate a unique secret, for example with `python -c "import secrets; print(secrets.token_urlsafe(50))"`.
   - `DJANGO_DEBUG`: `False`.
   - `DATABASE_URL`: the hosted PostgreSQL connection string, including its database, username, password, host, and SSL requirement. Do not use your local `localhost` URL.
   - `EMAIL_VERIFICATION_REQUIRED`: `False` while you want the current no-verification signup demo. Set it to `True` later only after configuring a real email backend.
   - `DJANGO_ALLOWED_HOSTS`: `.vercel.app` and any custom domain, comma-separated. Vercel preview hosts are also read from its `VERCEL_URL` variable.
   - `CSRF_TRUSTED_ORIGINS`: `https://*.vercel.app`; add your custom domain with `https://` when you use one.

4. Leave the **Build Command** and **Output Directory** at their defaults. Vercel reads root `requirements.txt` and `pyproject.toml`; Django static files are collected from `STATIC_ROOT` during the build.
5. Click **Deploy** and wait for the build to finish.
6. Apply database migrations against the hosted database before using the site. From your computer, temporarily set `DATABASE_URL` in a PowerShell session to the hosted URL, then run:

   ```powershell
   $env:DATABASE_URL = "YOUR_HOSTED_POSTGRESQL_URL"
   & .\.venv\Scripts\python.exe .\backend\manage.py migrate
   & .\.venv\Scripts\python.exe .\backend\manage.py seed_unimart
   Remove-Item Env:DATABASE_URL
   ```

   Keep the URL private and do not put it in source files. Alternatively, run migrations from a trusted deployment job using the same environment variable.

7. Open the Vercel deployment URL and test signup/login, product filters, product submission, and `/admin/`. Create the first admin account using a trusted one-off management command connected to the hosted database; never expose admin promotion in the public UI.

## Environment variables

Local development reads `backend/.env`. Production configuration is provided through the Vercel Project Settings and must not be committed. `DATABASE_URL` takes precedence over the local `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` variables.

If you later enable email verification, configure a production email service and its credentials as Vercel environment variables; the default console email backend only prints mail to server logs and is not a delivery service.

## Important limitations

- Vercel Functions are request-driven and do not provide a continuously running Django server.
- Product images currently use validated external image URLs; no upload storage has been configured.
- Demo products are local-only preview data. Production feeds contain only approved database listings.
- Local sample data is not a substitute for production inventory. Seed categories and universities with `seed_unimart`; real products must be submitted and approved by an administrator.
