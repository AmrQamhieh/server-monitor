# 📡 Server Monitor

A lightweight monitoring tool for **CPU, Memory, and Disk usage** on a remote Linux host.  
Metrics are collected via SSH, stored in a **MariaDB database**, and exposed through a **Flask REST API + Dashboard**.  
Runs entirely in **Podman/Docker containers**.

---
## ✨ Features
- Collects **CPU%, Memory%, Disk%** from a remote host
- Stores results in **MariaDB**
- REST API endpoints:
  - `/health` → check service status
  - `/latest` → latest metrics
  - `/last24hours` → stats for last 24h
  - `/cpu/...`, `/mem/...`, `/disk/...` → detailed views
- Web dashboard at `/`
- Unit tests with `unittest`
- Optional prebuilt image available on Docker Hub (amrqam/server-monitor:v1)
---

## 📦 Quick Start (Recommended)

### Clone & Configure
```bash
git clone https://github.com/amrqamhieh/server-monitor.git
cd server-monitor
```
---

## 🐳 Running with Podman Compose

Make sure you have **Podman** & **podman-compose** installed.

### 1️⃣ Prepare environment file
```bash
cp server-monitor.env.example server-monitor.env
```
Update your SSH & MariaDB credentials inside server-monitor.env:
```Env
HOST_IP=host.containers.internal
HOST_USER=root
HOST_PASSWORD=root
.....
```
✔ db is the name of the MariaDB service
✔ SSH settings allow the app container to read host usage
✔ Change passwords if needed

----
### 2️⃣ Create the logs folder
```bash
mkdir logs
```

### 3️⃣ Start the database + app
```bash
podman-compose up -d
```
This will start:
db → MariaDB

server-monitor-app → Flask API + Dashboard

---
### 3️⃣ Access the app
Dashboard → http://localhost:5001/

Health check → http://localhost:5001/health

Latest metrics → http://localhost:5001/latest

CPU Metrics → http://localhost:5001/cpu/current *OR* http://localhost:5001/cpu/last24hours

MEMORY Metrics → http://localhost:5001/mem/current *OR* http://localhost:5001/mem/last24hours

DISK Metrics → http://localhost:5001/disk/current *OR* http://localhost:5001/disk/last24hours

---
## 🧪 Running Unit Tests
Inside the virtual environment:
```bash
python3 -m unittest discover -s tests
```
---
## 🖥️ Running the Collector Manually
Collect one sample and insert it into MariaDB:
```bash
podman exec server-monitor-app python3 -m app.collector
```
Example output:
```json
{"cpu": 83.0, "mem": 37.5, "disk": 40.0}
```
---
### ⏱️ Automate Data Collection (host cronjob)
**Run cron on the host**
```bash
crontab -e
```
Add:
```bash
0 * * * * cd ~/server-monitor && podman exec server-monitor-app python3 -m app.collector
```
This runs the collector every hour.

____________________

### 🐳 Optional: Pull the Prebuilt Image
If someone doesn't want to build the app locally:
```bash
podman pull docker.io/amrqam/server-monitor:v1
```
or with Docker:
```bash
docker pull amrqam/server-monitor:v1
```
But note:

✔ You still need to clone the repo because podman-compose.yml defines the MariaDB service.

✔ The compose file currently builds locally (build: .), so Docker Hub image is optional.

____________________

## 🗂️ Project Structure
```bash
server-monitor/
│
├── app/
│   ├── app.py               # Flask API
│   ├── collector_job.py     # Collector script
│   ├── remote_usage.py      # SSH usage reader
│   ├── logging_utils.py     # Logging
│   └── templates/
│       └── dashboard.html
│
├── tests/                   # Unit tests
├── Dockerfile
├── podman-compose.yml
├── server-monitor.env       # (you create this)
├── requirements.txt
└── logs/                    # (must be created)

```


