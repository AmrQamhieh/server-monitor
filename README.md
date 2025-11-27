# 📡 Server Monitor

A lightweight monitoring tool for **CPU, Memory, and Disk usage** on a remote Linux host.  
Metrics are collected via SSH, stored in a **MariaDB database**, and exposed through a **Flask REST API + Dashboard**.  
Runs entirely in **Podman/Docker containers**.

---
## ✨ What You Get
- Collects **CPU%, Memory%, Disk%** from a remote host
- Stores results in **MariaDB**
- REST API endpoints:
  - `/health` → check service status
  - `/latest` → latest metrics
  - `/last24hours` → stats for last 24h
  - `/cpu/...`, `/mem/...`, `/disk/...` → detailed views
- Web dashboard at `/`
- Unit tests with `unittest`
- Ready‑to‑use image on Docker Hub:  
  `docker.io/amrqamhieh/server-monitor:v1`
---
## 📦 Project Structure
```bash
server-monitor/
│── app/
│   ├── app.py               # Flask API + dashboard
│   ├── collector.py         # Collect usage from remote host
│   ├── remote_usage.py      # SSH logic (Paramiko)
│   ├── logging_utils.py     # Logger + decorator
│   └── templates/
│       └── dashboard.html
│
│── tests/
│   ├── test_app.py
│   └── test_collector_job.py
│
│── Dockerfile
│── podman-compose.yml
│── requirements.txt
│── server-monitor.env.example
│── README.md
```


## 📦 Quick Start

### 1. Clone & Configure
```bash
git clone https://github.com/amrqamhieh/server-monitor.git
cd server-monitor
```
---

## 🐳 Option 1 - Running with Podman Compose

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
----

### 2️⃣ Start the database + app
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
### ⏰ Automating Collection (Cron)
**Run cron on the host**
```bash
crontab -e
```
Add:
```bash
0 * * * * cd ~/server-monitor && podman exec server-monitor-app python3 -m app.collector
```
____________________

### 🐳 Option 2 - Pulling From Docker Hub
Run the app directly from the published image:
```bash
podman pull docker.io/amrqam/server-monitor:v1
```
or with Docker:
```bash
docker pull amrqamhieh/server-monitor:v1
```
____________________

### 🏗️ Option 3 - Building the Image 
Rebuild from source:
```bash
podman build -t server-monitor .
```
____________

### 🗂️ What the App Container Looks Like Inside
If you run:
```bash
podman exec -it server-monitor-app bash
```
You'll see a very small and clean filesystem:
```bash
/app
│── app/
│   ├── app.py              # Flask API and dashboard routes
│   ├── collector.py        # Collects CPU/MEM/DISK via SSH
│   ├── remote_usage.py     # Paramiko SSH helper
│   ├── logging_utils.py    # Logging + decorator
│   └── templates/
│       └── dashboard.html
│
│── tests/
│   ├── test_app.py
│   └── test_collector_job.py
│
│── requirements.txt
│── server-monitor.env      # injected by podman-compose
│── __pycache__/            # Python compiled files
```

