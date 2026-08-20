# ClinicFlow — Local Testing Instructions

These instructions are for the current Phase 1 foundation. Use only synthetic/demo patient information while testing.

## Option A — One-click setup on Windows

1. Extract the ZIP to a simple location, for example:

   `C:\Project\ClinicFlow`

2. Confirm Python 3.12 or newer is installed:

   ```powershell
   py --version
   ```

3. Double-click `setup_and_run_demo.bat`.

4. Wait for the command window to display:

   `Starting development server at http://127.0.0.1:8000/`

5. Open this address in Chrome or Edge:

   `http://127.0.0.1:8000`

6. Sign in with:

   - Username: `admin`
   - Password: `ClinicFlow2026!`

Do not close the command window while testing. Press `Ctrl+C` in that window to stop the server.

## Option B — Manual setup with PowerShell

Open PowerShell inside the extracted ClinicFlow folder and run:

```powershell
py -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

If PowerShell blocks activation, run this once in the same window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

## Recommended test sequence

### 1. Test login

1. Open `http://127.0.0.1:8000`.
2. Sign in with the demo account.
3. Confirm the ClinicFlow dashboard opens.
4. Confirm the demo clinic name and today's appointment cards are visible.

Expected result: the login succeeds and the dashboard loads without an error.

### 2. Test the dashboard

Check the following:

- Total appointment count uses two digits, such as `03`.
- Confirmed, checked-in and completed cards display correctly.
- Today's appointment list shows patient, doctor, service, status and action buttons.
- The page remains usable when the browser window becomes narrow.

### 3. Create a future appointment

1. Select **New appointment**.
2. Choose a demo patient.
3. Choose **Dr. Ayesha Khan**.
4. Choose **General Consultation**.
5. Select a future date and time.
6. Select **Save appointment**.

Expected result:

- The appointment is saved.
- A success message appears.
- Reminder queue records are created for a consented patient.

Note: the current build creates reminder jobs but does not send real WhatsApp messages.

### 4. Test conflict prevention

1. Create an appointment for Dr. Ayesha Khan at a future time.
2. Try to create another appointment for the same doctor during the same 30-minute period.

Expected result: ClinicFlow blocks the second appointment and displays a doctor-conflict message.

### 5. Test appointment actions

On the dashboard:

1. Select **Confirm** for a scheduled appointment.
2. Select **Check in**.
3. Refresh the dashboard.

Expected result: the status and dashboard totals update.

Additional statuses—including completed, cancelled and no-show—can currently be tested through the Django Admin panel.

### 6. Test administration

1. Open `http://127.0.0.1:8000/admin/`.
2. Use the same demo login.
3. Review Clinics, Staff Profiles, Patients, Practitioners, Services, Appointments, Appointment Events and Reminders.

Expected result: all demo records are visible. Changes to production-style master data should be made only by authorized administrators.

### 7. Run automated checks

Stop the server with `Ctrl+C`, then run:

```powershell
venv\Scripts\Activate.ps1
python manage.py check
python manage.py test
```

Expected result:

```text
System check identified no issues
OK
```

## Reset the demo database

To start again with clean synthetic data:

1. Stop the server.
2. Delete `clinicflow_demo.sqlite3` from the project folder.
3. Run:

   ```powershell
   venv\Scripts\Activate.ps1
   python manage.py migrate
   python manage.py seed_demo
   python manage.py runserver
   ```

## Common problems

### `py` is not recognized

Install Python from `python.org`, enable **Add Python to PATH**, then reopen PowerShell.

### Port 8000 is already in use

Run the server on another port:

```powershell
python manage.py runserver 8005
```

Then open `http://127.0.0.1:8005`.

### `No module named django`

Activate the virtual environment and reinstall requirements:

```powershell
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Login does not work

Run the demo seed command again:

```powershell
python manage.py seed_demo
```

This resets the demo administrator password to `ClinicFlow2026!`.

## Important safety notes

- Do not enter real patient information into this development build.
- Do not expose the Django development server directly to the internet.
- Do not use the demo password in production.
- WhatsApp sending remains disabled until official Meta credentials, approved templates, signed webhooks and production consent controls are configured.
- This phase is appointment-management software, not an electronic medical record or medical-advice system.

## What to report after testing

For every issue, record:

- Page or feature
- Steps performed
- Expected result
- Actual result
- Screenshot
- Browser and Windows version
- Exact error shown in the command window

