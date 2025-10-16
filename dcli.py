#!/usr/bin/env python3
import click
import psutil
import subprocess
import socket
from datetime import datetime

# Command group
@click.group()
@click.version_option("1.0.0")
def cli():
    """
    DCLI: Data Center Sysadmin Toolkit

    This tool provides various utilities for sysadmins, focusing on
    resource monitoring and system diagnostics.
    """
    pass

# Network diagnostics
@cli.command()
@click.argument('hosts', nargs=-1, type=str)
@click.option('--ports', default='22,80,443', help='Ports to scan')
def netcheck(hosts, ports):
    """Ping hosts and check ports."""
    ports_list = [int(p) for p in ports.split(',')]
    for host in hosts or ['8.8.8.8']:  # Default Google DNS
        click.echo(f"Checking {host}...")
        try:
            subprocess.check_output(['ping', '-c', '1', host])
            click.echo("✅ Ping OK")
        except:
            click.echo("❌ Ping failed")
        for port in ports_list:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            status = "OPEN" if result == 0 else "CLOSED"
            click.echo(f"  Port {port}: {status}")

# Monitor system resources
@cli.command()
@click.option('--host', default='localhost', help='Target host to monitor. Currently only supports local monitoring.')
@click.option('--threshold-cpu', default=80, type=int, help='CPU usage percentage that triggers a red-colored alert.')
def monitor(host, threshold_cpu):
    """
    Monitor system resources (CPU, memory, and disk usage).

    This command takes a 1-second measurement of the local system's
    current resource utilization and prints the results to the console.
    It will show a high CPU alert if the usage exceeds the specified
    threshold.
    """
# ... (rest of the monitor function)

if __name__ == '__main__':
    cli()