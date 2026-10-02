# NexspireCRM

NexspireCRM is a FastAPI and MongoDB CRM with a same-origin vanilla JavaScript
workspace.

## Run locally

Configure `MONGODB_URL`, `DATABASE_NAME`, `SECRET_KEY`, `ALGORITHM`,
`ACCESS_TOKEN_EXPIRE_MINUTES`, and `REFRESH_TOKEN_EXPIRE_DAYS` in `.env`, then
start the API from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/` for the public Nexspire Technologies website.
Use the sign-in icon in the site header to open the existing login and
registration page at `/login.html`. After signing in, each account is sent to
the CRM dashboard at `/index.html`; the **Company** link in the dashboard
returns to the public website. The company site is also available at
`/company.html`.

The first registered account becomes the workspace Admin; subsequent public
registrations receive the Viewer role. Admins can add team members, create
roles, and edit role permissions in **Admin Center**. The built-in role set is
created during registration; existing workspaces can use `POST /roles/seed` to
add any missing built-in roles.

Role permissions for dashboards, leads, customers, and follow-ups are checked
by the API as well as used to show the matching workspace sections and actions.
Built-in roles have sensible defaults, and Admin always retains full access.
The editable permission set includes `dashboard.view` and view/create/update/
delete/convert capabilities for leads, customers, and follow-ups (conversion is
lead-only). Role changes are enforced by the API on the next request.

Follow-ups keep their subject, scheduled date, and notes as separate fields.
Existing follow-ups are backfilled from their saved remarks at startup, with
the original remarks retained for compatibility.

## Focused validation

```powershell
.\.venv\Scripts\python.exe test_auth.py
```
