# DC2LI - Data Center CLI Toolkit

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
cd dc2li
```
### Install dependencies:
pip install click psutil paramiko

## Usage

Run the tool with `python3 dcli.py` followed by a command. Use `--help` for details on each command.

## Examples

### MONITORING
```
python3 dcli.py monitor                                    # Local system
python3 dcli.py monitor --host IP --user USER --password PASS  # Remote
```
### NETWORK
```
python3 dcli.py netcheck HOST1 HOST2                      # Multiple hosts
python3 dcli.py netcheck HOST --ports 80,443,3306         # Custom ports
```
### LOGS
```
python3 dcli.py logs /path/to/logfile                     # View logs
python3 dcli.py logs /path/to/logfile --errors-only       # Errors only
```
### HELP
```
python3 dcli.py --help                                    # All commands
```

<p align="center"> <em>Built with ❤️ for data center professionals</em> </p>
