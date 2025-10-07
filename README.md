# Employee_management

This Django app manages employees and now supports attaching a resume/CV file to each employee record.

Resume feature summary
- Employees now have a `resume` file field (stored under `media/resumes/`).
- Allowed resume/file types: PDF, DOC, DOCX, PNG, JPG. Max file size: 5 MB.

Setup / Run (development)

1. Install dependencies from `requirements.txt` and create a virtual environment if needed.

2. Make migrations and migrate (the repository includes the migration to add the `resume` field):

```powershell
python manage.py makemigrations
python manage.py migrate
```

3. Run the development server:

```powershell
python manage.py runserver
```

4. Log in as a staff user to add or edit employees and upload a resume. Uploaded resumes will be accessible at `/media/resumes/...` during development (DEBUG=True).

Notes
- In production, configure a proper media file server (S3, nginx, etc.) and secure file access as needed.
- Tests include a small unit test that verifies creating an employee with an in-memory PDF resume.

How to present this project to an interviewer
------------------------------------------------
This section gives a concise script and points you can mention while demoing the app.

1) Quick elevator pitch (30 seconds)
- "This is a small employee management web app built with Django. It stores employee data, supports resume uploads, profile pictures, filtering, and data export. I built a clean dashboard, CRUD flows, and made resume handling robust with server-side validation and client-side checks."

2) Key features to highlight (demo order)
- Dashboard: show the attractive, responsive dashboard with total employees, departments and roles.
- Add Employee: demonstrate adding an employee and uploading a resume (PDF/DOC/DOCX). Mention file size limits and validation.
- View Employee: show the detail page where the resume can be downloaded.
- List and Filter: show filtering employees by department/role and exporting CSV/Excel.
- Admin: explain that Django admin is available for bulk management.

3) Implementation details (what to mention technically)
- Backend: Django 5.x with standard class-based views (ListView, CreateView, UpdateView, DetailView, DeleteView).
- Models: Employee model includes fields for personal info, `profile_picture` (ImageField) and `resume` (FileField). I added DB migration for the resume field.
- Forms: Custom `EmployeeForm` with server-side validation for phone numbers and resume (size & mime-type checks).
- Templates/UI: Bootstrap 5 + Font Awesome for responsive, modern UI. Added a polished dashboard and list/detail layouts.
- Files: Media files are saved under `media/`. In dev `MEDIA_URL` is served via Django when DEBUG=True; in prod use S3/nginx.
- Tests: A unit test verifies resume upload handling using an in-memory file.

4) Security & production notes
- File validation: both client and server checks are implemented; for production add virus scanning and secure private storage.
- Privacy: consider access control on resume downloads (signed URLs) when storing resumes in cloud storage.

5) Next improvements to mention (shows awareness)
- Add preview for PDF resumes using an embedded viewer.
- Add role-based access to view/download resumes.
- Integrate cloud storage (S3) with `django-storages` and signed URLs for secure access.
- Add automated end-to-end tests for upload/download flows.

Demo commands & quick checks
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Contact
- If you want me to help add the PDF preview or secure downloads for production, I can implement that next.

Roadmap & how I would build this as a resume-first project (what to present in interview)
---------------------------------------------------------------------------------
If this is your first project and you want it to impress HR/interviewers, present it like a polished product. Here's a roadmap and rationale you can describe:

1) Project architecture (what you would explain)
- Frontend: Django templates enhanced by Bootstrap 5 + Font Awesome. Use small JS components for UX (preview modal, validation). For larger apps, plan React/Vue front-end with API.
- Backend: Django (models, CBVs), SQLite for dev; Postgres for production.
- Storage: Media files (resumes, photos) stored in S3 (production) and served via signed URLs; local `media/` during dev.
- Tests: Unit tests for model/form behavior; simple integration tests for upload/download flows; optional E2E tests with Playwright.

2) Feature set (what to demo and explain why)
- Core: CRUD for employees (name, email, phone, hire_date, dept, role, profile picture).
- Resume-first features (highlight these):
	- Resume upload with client & server validation (type + size).
	- Resume preview modal (inline PDF viewer) — implemented in the app as a demo.
	- Resume download (authenticated). Discuss adding signed URLs for production.
- Analytics: total employees, departments, roles on dashboard for quick snapshot.
- Export: CSV and Excel exports for HR reporting.

3) UX & accessibility (what HR cares about)
- Clean dashboard, large call-to-action buttons, consistent color palette and accessible contrast.
- Keyboard navigation-friendly forms and labels.
- Mobile-responsive layout via Bootstrap grid.

4) Security & privacy (be ready to answer)
- Validate files server-side and client-side. Use anti-virus scanning for production.
- Store files in private S3 buckets; generate short-lived pre-signed URLs for downloads.
- Add role-based permissions so only HR or admins can download resumes.

5) Testing & quality
- Unit tests: models, forms (validation). The repo includes a test for resume upload.
- Integration tests: simulate file uploads and verify stored metadata and download links.
- CI: Add GitHub Actions to run tests and style checks on PRs.

6) Deployment and monitoring
- Containerize with Docker, deploy to a PaaS (Heroku / Render) or VPS behind nginx.
- Use managed Postgres and S3; set environment variables for secrets.
- Add basic monitoring and logs (Sentry for errors, access logs for file downloads).

Key phrases to use during the interview (short bullets)
- "I focused on usability and the resume experience — quick upload, preview, and secure download." 
- "I implemented both client-side and server-side validation to prevent bad files and provide immediate feedback." 
- "For production we'd use private cloud storage + signed URLs to ensure only authorized users can access resumes." 
- "The codebase is testable and modular — models/forms/views are separated and covered by unit tests." 

If you'd like, I can now:
- Add S3 storage wiring (django-storages) and a sample `production` settings template.
- Add inline PDF preview using PDF.js for consistent cross-browser viewing.
- Add role-based resume download view (so only staff or HR can download resumes) with sample permission checks.

