# PaaS Deployment Reproduction Guide

## Student Management System using Render and GitHub

**Purpose:** This guide documents how to deploy the Flask Student
Management System as a Platform as a Service (PaaS) application using
Render. It is intended to accompany the IaaS reproduction guide for the
AWS EC2 deployment.

> **Status note:** These are reproduction instructions for the planned
> Render deployment. Completing the steps below is what creates the live
> Render service; this guide does not claim that a Render deployment has
> already succeeded.

------------------------------------------------------------------------

## 1. Objective

Deploy the same Student Management System used in the IaaS lab, but this
time without manually managing a virtual machine or configuring its
operating system.

The application uses: - **Python** for application logic. - **Flask** as
the web framework. - **HTML** for the user interface. - **Gunicorn** as
the production WSGI server. - **GitHub** to store and provide the source
code to Render. - **Render** to build and host the web application.

### Expected result

After deployment, Render provides a public URL, usually ending in
`onrender.com`. Opening that URL should display the Student Management
System.

## 2. IaaS versus PaaS in this lab

  -----------------------------------------------------------------------
  Area                    IaaS: AWS EC2           PaaS: Render
  ----------------------- ----------------------- -----------------------
  Infrastructure          A virtual machine is    Hosting infrastructure
                          provided                is managed by Render

  Operating system        We configured Ubuntu    OS management is mostly
                                                  abstracted away

  Application setup       We installed Python,    Render installs
                          dependencies, and       dependencies using the
                          Gunicorn                build command

  Process management      We configured Gunicorn  Render runs the
                          with systemd            configured start
                                                  command

  Network access          We configured an EC2    Render provides a web
                          security group and port endpoint and manages
                          8000                    the hosting network

  Deployment workflow     SSH into the instance   Connect a GitHub
                          and configure it        repository and deploy

  Control                 More control over the   Less infrastructure
                          VM and OS               control, less server
                                                  administration
  -----------------------------------------------------------------------

PaaS reduces the amount of infrastructure administration required. It
does not mean the developer has no configuration responsibilities: the
code, dependencies, build command, start command, and application
behavior still need to be correct.

## 3. Files required

Start with the project ZIP, `student_management_ec2_copy.zip`, and
extract it on your local computer.

The repository should have this structure:

``` text
student-management-cloud-lab/
├── application.py
├── requirements.txt
├── Procfile
├── README.md
├── .gitignore
└── templates/
    └── index.html
```

The reproduction guide may also be kept in the repository, if desired.

### What each file does

-   `application.py`: Defines the Flask application and the route that
    displays and accepts student records.
-   `templates/index.html`: Contains the HTML form and table used by the
    web interface.
-   `requirements.txt`: Lists Python packages that must be installed.
-   `Procfile`: Documents a process start command. The Render dashboard
    start command below is the authoritative setting for this guide.
-   `README.md`: Provides basic project information.
-   `.gitignore`: Excludes files that should not be committed, such as a
    local virtual environment.

Before uploading, verify that `application.py` is at the repository
root, that it exposes the Flask object as `app`, and that
`templates/index.html` is in the `templates` directory.

### Dependencies

Open `requirements.txt` and confirm that it includes at least:

``` text
Flask
gunicorn
```

If the file already contains valid version pins, you can keep them. Do
not add unrelated packages that the application does not use.

## 4. Prepare the GitHub repository

Render deploys the code from a repository. You do not upload the ZIP
directly to a Render web service.

### Option A: Upload using the GitHub website

1.  Sign in to GitHub.
2.  Create a new repository named `student-management-cloud-lab`.
3.  Choose public or private according to your preference. If you choose
    private, authorize Render to access it.
4.  Extract `student_management_ec2_copy.zip`.
5.  Upload the project files and folders to the repository.
6.  Confirm the repository root contains `application.py` and
    `requirements.txt`, and that `templates/index.html` exists.

Avoid uploading your `.venv` directory, Python cache files, passwords,
access keys, or other secrets.

### Option B: Push with Git

Open a terminal in the extracted project directory and run:

``` bash
git init
git add .
git commit -m "Prepare student management app for PaaS deployment"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the actual URL shown by
GitHub. If the repository is already a Git repository, do not run
`git init` again unnecessarily. If Git asks you to authenticate, follow
GitHub's current authentication process.

After pushing, open the repository in your browser and verify that the
files and folder structure are correct.

## 5. Create a Render Web Service

1.  Open the Render dashboard: <https://dashboard.render.com/>.
2.  Sign in or create an account.
3.  Connect your GitHub account if prompted.
4.  Choose **New** and then **Web Service**.
5.  Select the `student-management-cloud-lab` repository.
6.  Configure the service using the settings below.

### Render settings

  --------------------------------------------------------------------------------------------------------------
  Setting                             Value
  ----------------------------------- --------------------------------------------------------------------------
  Service type                        Web Service

  Runtime/language                    Python, if shown as a selectable runtime

  Build command                       `pip install -r requirements.txt`

  Start command                       `gunicorn application:app --workers 1 --timeout 60 --bind 0.0.0.0:$PORT`

  Instance plan                       Choose an available plan appropriate for a lab demonstration
  --------------------------------------------------------------------------------------------------------------

The exact dashboard labels and available plans may change. Review
Render's current pricing, limits, and account requirements before
selecting a plan.

### Why this start command?

-   `gunicorn`: Starts the production WSGI server.
-   `application:app`: Imports the Flask object named `app` from
    `application.py`.
-   `--workers 1`: Uses one worker for this small demonstration app.
-   `--timeout 60`: Sets a worker timeout of 60 seconds.
-   `--bind 0.0.0.0:$PORT`: Listens on all interfaces using the port
    supplied by Render.

Do not hard-code port `8000` for Render. Render supplies the port
through the `PORT` environment variable.

7.  Review the configuration and click **Create Web Service** (the exact
    button wording may vary).
8.  Open the deployment logs and wait for the build and deployment to
    finish.
9.  When Render shows the service as live, open the public URL provided
    on the service page.

## 6. Test the deployed application

Use only dummy data for this lab.

1.  Open the Render public URL.
2.  Confirm that the Student Management System page loads.
3.  Confirm the initial sample student records appear.
4.  Enter a test student's name and course.
5.  Submit the form.
6.  Check whether the page redirects and the new record appears.
7.  Refresh the page and observe whether the record remains.
8.  If the service has been idle, allow for a possible wake-up delay
    depending on the chosen hosting plan.

**Important:** The current demo stores records in a Python in-memory
list. This is not persistent storage. Records can disappear after a
restart, redeployment, or when the hosting process changes. A successful
form submission during one test does not establish that the app has a
persistent database.

## 7. Evidence to capture for the lab report

Capture screenshots after the deployment has actually succeeded:

-   GitHub repository showing the project files.
-   Render service configuration showing the build and start commands.
-   Render deployment log showing a successful build and start.
-   Render service page showing its live status and public URL.
-   The application open at the public URL.
-   A test student displayed after submitting the form.

Do not include access tokens, credentials, or private information in
screenshots. Do not use real student information.

## 8. Troubleshooting

### A. Build fails because a dependency is missing

1.  Open the Render service's deployment logs.
2.  Check that `requirements.txt` exists at the repository root.
3.  Confirm it includes Flask and Gunicorn.
4.  Commit and push any correction to GitHub.
5.  Trigger a new deployment in Render if automatic deployment does not
    start.

### B. The application fails to start

Check the start command carefully:

``` bash
gunicorn application:app --workers 1 --timeout 60 --bind 0.0.0.0:$PORT
```

Confirm: - The file is named `application.py`. - The Flask variable is
named `app`. - The repository root contains `application.py`. -
`gunicorn` is in `requirements.txt`.

If the file is named differently or the Flask object has a different
name, the start command must match the actual file and variable names.

### C. The page returns an error

1.  Open the Render logs for the latest deployment.
2.  Look for Python tracebacks or import errors.
3.  Check that the `templates` directory and `index.html` are present
    and correctly named.
4.  Test the same project locally to help separate application problems
    from deployment configuration problems.

### D. Changes do not appear

1.  Verify the changes were committed and pushed to the connected GitHub
    branch.
2.  Check the latest deployment status in Render.
3.  Confirm the service is deploying the intended repository and branch.
4.  Review build and runtime logs.

### E. Student records disappear or appear inconsistently

This is expected to be possible with the current in-memory
implementation. It does not use a database. For persistent data, update
the application to use a database such as PostgreSQL and configure it
correctly for the hosting environment. Do not treat the current
demonstration as a production student-record system.

### F. The service is slow to respond after being idle

Some hosting plans may suspend or scale down idle services, causing a
delay on the next request. Check the behavior and limits of the plan
currently selected in Render. Do not assume every plan has the same idle
behavior.

## 9. How to run the app locally

You can test the extracted project locally before or after deploying it.

### Windows PowerShell

Open PowerShell in the project directory:

``` powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python application.py
```

If PowerShell blocks virtual-environment activation, you can use the
environment's Python executable directly:

``` powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe application.py
```

Open the local URL printed by Flask. In the supplied application, the
development server normally uses:

`http://127.0.0.1:5000/`

Stop the local server with `Ctrl+C`.

### Ubuntu/Linux

From the project directory:

``` bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python application.py
```

Open the local URL printed by Flask. Stop the server with `Ctrl+C`.

## 10. What is managed by Render and what is managed by you?

### Render manages

-   The underlying hosting infrastructure.
-   The deployment environment and build process.
-   Starting the web service using the configured start command.
-   Providing the service endpoint and platform logs.

### You manage

-   The Flask source code and HTML template.
-   Python dependencies.
-   The build and start commands.
-   Testing and application-level debugging.
-   Data design, security, and any persistent database.
-   Choosing a suitable plan and monitoring its usage or limits.

The exact responsibilities and features depend on Render's current
product and plan.

## 11. Cost and shutdown considerations

Review the current Render plan before deploying. Pricing, free-tier
eligibility, usage limits, sleep behavior, and service availability can
change.

When you finish the demonstration: 1. Save your screenshots and
deployment details. 2. Keep the project on your local computer and in
GitHub. 3. If you no longer need the hosted service, use Render's
dashboard to suspend or delete the service according to the options
available for your plan. 4. Check whether any related paid resources
remain active.

Deleting or suspending a Render service is separate from stopping your
AWS EC2 instance. The PaaS service runs independently of EC2, so the EC2
instance can remain stopped while Render is used.

## 12. Conclusion

In this lab, the Student Management System is hosted using a PaaS
platform. Rather than configuring an operating system and managing a
server directly as in the EC2 IaaS deployment, the developer provides
the application code and deployment settings while Render manages much
of the hosting infrastructure.

This demonstrates the main distinction between IaaS and PaaS: IaaS
offers more direct infrastructure control, while PaaS reduces
server-management work and provides a more streamlined application
deployment workflow.

**Scope limitation:** This is a teaching/demo application. It uses
in-memory records and does not provide authentication or persistent
database storage. It should not be used to store real student records.
