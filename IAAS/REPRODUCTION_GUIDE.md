# Reproduction Guide: Student Management System on AWS EC2

This guide consolidates the workflow used to host a small Flask Student Management System on an Ubuntu EC2 virtual machine. It covers the app files, local execution, EC2 setup, the systemd service, testing, troubleshooting, and safe shutdown.

## 1. What the application does

The app has one page at `/` with a form for a student's name and course/department. Submitting the form sends an HTTP POST request. Flask appends the values to a Python list and redirects the browser back to the home page. The page renders the current list in a table.

The two initial demonstration records are:

- Aarav Sharma, Computer Engineering
- Mira Patel, Information Technology

This is a lab demo, not a production student information system. It has no database or login and should not be used with real personal data.

## 2. Files and their roles

- `application.py`: creates the Flask app, defines the GET/POST route, and holds the in-memory student list.
- `templates/index.html`: HTML and CSS for the form and table. The form field names must match the names read in `application.py` (`name` and `course`).
- `requirements.txt`: Python packages Flask and Gunicorn.
- `Procfile`: an example process declaration for compatible hosting platforms. It is not required for the systemd setup on EC2.
- `student-management.service.example`: reference systemd unit for the EC2 deployment. It uses the `ubuntu` account, the project directory `/home/ubuntu/student-management`, Gunicorn, and port 8000.
- `.gitignore`: excludes the virtual environment, Python bytecode, and local secrets/logs from Git.

## 3. Run the app on your own computer

Install Python 3.10 or newer, extract the project ZIP, and open a terminal in the extracted project directory.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python application.py
```

Visit `http://127.0.0.1:5000` in your browser. Stop the development server with Ctrl+C in the terminal.

### Ubuntu/Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python application.py
```

Visit `http://127.0.0.1:5000`. Stop it with Ctrl+C.

## 4. Create and connect to the EC2 instance

1. Sign in to the AWS Management Console and open **EC2**.
2. Launch an instance using an Ubuntu Server AMI. The lab instance used Ubuntu and the default login user `ubuntu`.
3. Choose an instance type suitable for a small demo. A small/free-tier-eligible type may be enough where eligible, but check current AWS pricing and free-tier eligibility for your account and region.
4. Configure a key pair or another supported connection method.
5. In the instance's security group, add inbound rules as needed:
   - **SSH (TCP 22):** restrict to your current public IP or use the AWS-supported EC2 Instance Connect setup appropriate to your instance and region.
   - **Custom TCP (TCP 8000):** for browser access, restrict the source to your current public IP (`My IP`) when possible. Opening it to `0.0.0.0/0` allows the whole internet to reach that port and is not recommended for an unauthenticated demo.
6. Launch the instance and connect using EC2 Instance Connect or SSH.

Security group rules and public IPs can change. Do not assume an old IP address or old inbound rule will remain valid.

## 5. Install the runtime on Ubuntu EC2

After connecting to the instance, update packages and install Python, pip, and the virtual-environment module:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

Check the installed Python version:

```bash
python3 --version
```

## 6. Copy the project onto EC2

There are multiple valid ways to transfer the files, including `scp`, uploading a ZIP, or creating the files in the EC2 terminal. The deployment directory used in this lab is:

```bash
mkdir -p ~/student-management/templates
cd ~/student-management
```

Place `application.py`, `requirements.txt`, and the `templates/index.html` file there. Make sure the directory structure is exactly:

```text
student-management/
├── application.py
├── requirements.txt
├── Procfile
└── templates/
    └── index.html
```

If transferring a ZIP, upload it to the instance and extract it so `application.py` is directly inside `~/student-management`, not nested inside an extra directory.

## 7. Create a virtual environment and install packages

Run on EC2:

```bash
cd ~/student-management
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Check that Gunicorn is available:

```bash
.venv/bin/gunicorn --version
```

## 8. Test the application before configuring systemd

Run the development server temporarily:

```bash
python application.py
```

The app listens on port 5000 in development mode. If you want to test from your computer, you would need a matching security group rule for TCP 5000; alternatively test locally on the instance. Stop it with Ctrl+C before starting the production service. Do not run both servers on the same port simultaneously.

A local health check for the development server is:

```bash
curl -I http://127.0.0.1:5000/
```

## 9. Configure Gunicorn with systemd on EC2

The EC2 service uses port 8000 and is managed by systemd so it can run in the background and start after a reboot.

Create the unit file:

```bash
sudo nano /etc/systemd/system/student-management.service
```

Use this configuration (adjust paths or user only if your deployment differs):

```ini
[Unit]
Description=Student Management System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/student-management
Environment="PATH=/home/ubuntu/student-management/.venv/bin"
ExecStart=/home/ubuntu/student-management/.venv/bin/gunicorn --workers 1 --timeout 60 --bind 0.0.0.0:8000 application:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Save in Nano with Ctrl+O, Enter, then Ctrl+X. Then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now student-management.service
sudo systemctl status student-management.service --no-pager
```

If you later change the service file, run `sudo systemctl daemon-reload` and restart the service. If you edit Python or template files, restart the service so the running process picks up the changes:

```bash
sudo systemctl restart student-management
```

The one-worker, 60-second-timeout command is the temporary stabilization configuration used after observing Gunicorn worker timeouts. It does not make in-memory records persistent.

## 10. Test the EC2 service

First test from the instance itself:

```bash
curl -I http://127.0.0.1:8000/
```

A healthy response should show an HTTP status such as `200 OK`.

Test the form handler with a fictional record:

```bash
curl -i --max-time 10 -X POST http://127.0.0.1:8000/ \
  -d "name=Test Student&course=Testing"
```

A `302 FOUND` response with `Location: /` is expected because the app redirects after processing a form submission. To see whether that record is in the current process's memory, run:

```bash
curl -s http://127.0.0.1:8000/ | grep -i "Test Student"
```

Then open the instance's public IPv4 address in your browser using HTTP and port 8000:

```text
http://YOUR_EC2_PUBLIC_IPV4:8000/
```

Replace the placeholder with the instance's current public IPv4 address. Do not use `https://` because HTTPS/TLS was not configured in this demo. The public IP may change after a stop/start unless you have configured an Elastic IP.

## 11. Useful commands for checking the service

```bash
# Current service state
sudo systemctl status student-management --no-pager

# Recent application/service logs
sudo journalctl -u student-management -n 100 --no-pager

# Follow logs live
sudo journalctl -u student-management -f

# Restart the service
sudo systemctl restart student-management

# Stop the service
sudo systemctl stop student-management

# Start the service
sudo systemctl start student-management

# Check the local HTTP response
curl -I http://127.0.0.1:8000/
```

The earlier logs included Gunicorn `WORKER TIMEOUT` messages and traces where a worker was waiting to read a request. Gunicorn's text `Perhaps out of memory?` is a warning and does not, by itself, prove that the instance ran out of memory. The POST test returned `302 FOUND`, and a subsequent GET showed `Test Student` in the response.

## 12. Why records can disappear or look inconsistent

The list called `students` exists only in process memory. It is not stored in SQLite, MySQL, or another database. Restarting the service resets it to the two hard-coded sample records. Multiple Gunicorn workers would each have separate copies of that list, which can cause inconsistent results; the service was changed to one worker as a temporary workaround. A database such as SQLite is the appropriate next improvement if persistent records are required.

## 13. IaaS, PaaS, and SaaS connection for the lab report

- **IaaS:** EC2 provides the virtual machine. You manage the OS, Python environment, web server process, app files, and network rules.
- **PaaS:** A platform such as AWS Elastic Beanstalk manages more of the deployment environment. This same Flask app can be packaged for a compatible Python environment, but that is a separate deployment and was not part of the EC2 deployment described here.
- **SaaS:** A ready-made product such as Google Forms can demonstrate a similar data-collection workflow. It is not the same custom Flask application and does not mean this app was deployed as SaaS.

## 14. Can you stop the EC2 instance now?

Yes, if you have saved the required photos/screenshots and no longer need the website running right now, you can stop the instance from the EC2 console. Choose **Instance state → Stop instance**. Do not choose **Terminate instance**, which deletes the instance and its associated instance-store data and can make the VM unrecoverable. Stopping an EBS-backed instance normally preserves its EBS root volume and files, including this app, but check the storage configuration and any important data first.

Important points:

- While stopped, the website is unavailable.
- Compute charges generally stop for a stopped instance, but attached EBS volumes and some other resources can still incur charges. Review current AWS pricing and the resources in your account.
- A regular public IPv4 address can change after the instance is started again, so check the new address and update your browser URL/security group source if necessary.
- If you want to continue the demo later, start the same instance, wait for its status checks, confirm the service with `sudo systemctl status student-management`, and test the current public IP on port 8000.
- Do not terminate the instance unless you are sure you no longer need the VM. Download this project ZIP to your own device as a backup.

## 15. Limitations and safety

This is a teaching demo with no authentication, no database, no HTTPS, and an in-memory list. Use fictional data only. Before making it available to others, restrict inbound network access and add appropriate authentication, persistence, and TLS.
