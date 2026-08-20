# ClinicFlow

ClinicFlow is a Pakistan-focused clinic appointment and reminder operations platform. This repository begins Phase 1 with secure staff access, patient/service/doctor setup, conflict-aware appointment booking, reminder job creation, appointment status tracking, audit events, and a live clinic dashboard.

## Quick start (Windows PowerShell)

```powershell
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations core
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open `http://127.0.0.1:8000` and sign in with the synthetic demo account:

- Username: `admin`
- Password: `ClinicFlow2026!`

Change this password immediately outside a local demo.

## Current Phase 1 foundation

- Clinic-scoped staff roles
- Patient, practitioner and service masters
- Appointment conflict validation and lifecycle
- Consent-aware reminder queue records
- Reception dashboard and quick status actions
- Appointment event audit history
- PostgreSQL-ready production settings
- Synthetic demo data only

## Safety boundary

This initial build is not an electronic medical record and does not provide diagnosis, prescriptions, clinical advice, or autonomous AI responses. WhatsApp sending remains disabled until official Meta credentials, approved utility templates, webhook verification, consent wording and production controls are configured.

## Next build increment

1. Generate and commit deterministic migrations.
2. Add schedule/leave rules and week calendar.
3. Add Celery + Redis worker and idempotent reminder dispatcher.
4. Integrate official WhatsApp Cloud API and signed webhooks.
5. Add management KPI dashboard, date filters and drill-down.
6. Add permissions tests, audit views, exports, CI and deployment configuration.
