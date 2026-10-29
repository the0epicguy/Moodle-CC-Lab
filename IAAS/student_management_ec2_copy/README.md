# Student Management System: AWS EC2 Cloud Computing Lab

A small Flask web application for demonstrating hosting a web application on an AWS EC2 virtual machine (IaaS). It lets a user add a student name and course/department and view the records in a table.

## Files

- `application.py`: Flask routes and sample records.
- `templates/index.html`: web form and student table.
- `requirements.txt`: Python dependencies (Flask and Gunicorn).
- `Procfile`: example process command for compatible deployment platforms.
- `student-management.service.example`: systemd service template used for an Ubuntu EC2 host.
- `REPRODUCTION_GUIDE.md`: detailed reproduction notes for the lab.

## Run locally

Requires Python 3.10 or newer.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python application.py
```

Open http://127.0.0.1:5000.

### Linux or macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python application.py
```

Open http://127.0.0.1:5000.

## Important limitations

- Student records are stored in a Python list in process memory, not in a database.
- Records added during a session can be lost when the app or service restarts.
- The application has no login, authentication, authorization, or HTTPS configuration. Use only fictional/demo data.
- The EC2 systemd configuration serves the app on port 8000; the local development command serves it on port 5000.

See `REPRODUCTION_GUIDE.md` for the step-by-step AWS process and shutdown guidance.
