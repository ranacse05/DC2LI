# DCLI - Data Center CLI Toolkit

<p align="center">
  <strong>A Python-based command-line tool designed to automate routine system and network tasks</strong>
</p>

> **Ideal for data center administrators** managing servers, performing security checks, and handling backups. Tailored to enhance efficiency in data center operations.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **System Monitoring** | Check CPU, memory, disk usage, and uptime with customizable alert thresholds |
| **Network Diagnostics** | Ping hosts and scan common ports (22, 80, 443 by default) |
| **Log Analysis** | Tail and filter logs for errors or anomalies |
| **Security Audit** | Perform basic checks for outdated packages or weak configurations |
| **Backup Management** | Sync files or directories to a destination |
| **Patch Verification** | Simulate package updates for verification |
| **User Management** | Add, remove, or list users on the system |
| **Forensics Quick-Scan** | Generate file hashes and modification timestamps |

---

## 📥 Installation

### Clone the repository:
```
git clone https://github.com/ranacse05/dcli.git
cd dcli
```
### Install dependencies:
pip install click psutil paramiko

## Usage

Run the tool with `python3 dcli.py` followed by a command. Use `--help` for details on each command.

### Examples

**Monitor System Resources:**
python3 dcli.py monitor --threshold-cpu 70

text
Output: Displays CPU, memory, and disk usage; alerts if CPU exceeds 70%.