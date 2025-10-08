# Employee_management

This Django app manages employees and now supports attaching a resume/CV file to each employee record.

Resume feature summary
- Employees now have a `resume` file field (stored under `media/resumes/`).
- Allowed resume/file types: PDF, DOC, DOCX, PNG, JPG. Max file size: 5 MB.

# Employee Management System

A lightweight Django application to manage employees, upload and preview resumes, and provide HR-focused analytics.

Features
 - Employee CRUD (Create / Read / Update / Delete) with authentication and staff-only editing.
 - Resume upload (FileField) with client- and server-side validation (allowed: PDF, DOC, DOCX, PNG, JPG; max 5 MB).
 - Profile pictures (ImageField) and media handling in development.
 - Search, filter, and paginated employee list.
 - CSV / Excel export (CSV, XLSX).
 - Dashboard analytics (hires by month, employees by department, salary distribution) generated with pandas + matplotlib.

Quick start (development)

1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Apply migrations and create a superuser

```powershell
python manage.py migrate
python manage.py createsuperuser
```

4. Run the development server

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/ and log in with the superuser to manage employees.

Notes about charts
 - Charts are generated server-side using pandas + matplotlib and embedded as base64 PNGs on the dashboard for compatibility.
 - If your environment does not have seaborn styles installed, the code falls back to safe rcParams so charts render consistently.

Testing
 - A minimal test exists for resume upload. Run:

```powershell
python manage.py test
```

Production considerations
 - Use a production database (Postgres / MySQL) and configure `settings.py` appropriately.
 - Store media files (resumes/photos) in a cloud storage backend (S3) with `django-storages` and serve via signed URLs for security.
 - Add virus scanning for uploaded files and restrict resume download to authorized roles.

Next improvements (recommended)
 - Convert charts to interactive Chart.js visuals loaded via AJAX for a better UX.
 - Add role-based access controls for resume downloads.
 - Add CI (GitHub Actions) to run tests on push/PR and a caching layer for generated charts.

Contact
If you want, I can implement S3 integration, interactive charts, or role-based resume access next — tell me which and I’ll add it.


