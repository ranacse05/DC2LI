import click
import paramiko
import subprocess
import socket
import psutil
from datetime import datetime


# Shared SSH helper
def ssh_connect(host, user, key_path=None, password=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if key_path:
        client.connect(host, username=user, key_filename=key_path)
    elif password:
        client.connect(host, username=user, password=password)
    else:
        raise ValueError("Provide key_path or password for SSH")
    return client

@click.group()
def cli():
    """A simple system diagnostic and monitoring CLI tool."""
    pass


#Network diagnostics
@cli.command()
@click.argument('hosts', nargs=-1, type=str)
@click.option('--ports', default='22,80,443',
              help='Comma-separated list of ports to scan for each host (default: 22,80,443).')
def netcheck(hosts, ports):
    """
    Ping one or more hosts and check the status of common ports.

    This command sends a single ping to each host and then attempts
    to connect to the specified ports to determine whether they are open
    or closed.

    \b
    Examples:
      cli.py netcheck 8.8.8.8 example.com
      cli.py netcheck localhost --ports 22,8080,3306
    """
    ports_list = [int(p) for p in ports.split(',')]
    for host in hosts or ['8.8.8.8']:  # Default Google DNS
        click.echo(f"Checking {host}...")
        try:
            subprocess.check_output(['ping', '-c', '1', host])
            click.echo("Ping OK")
        except subprocess.CalledProcessError:
            click.echo("Ping failed")

        for port in ports_list:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            status = "OPEN" if result == 0 else "CLOSED"
            click.echo(f"  Port {port}: {status}")


#Monitor system resources
@cli.command()
@click.option('--host', default='localhost',
              help='Target host to monitor (currently only supports local monitoring).')
@click.option('--threshold-cpu', default=80, type=int,
              help='CPU usage percentage that triggers a red-colored alert (default: 80).')
def monitor(host, threshold_cpu):
    """
    Monitor system resources such as CPU, memory, and disk usage.

    This command performs a 1-second measurement of the local system’s
    current resource utilization and prints the results to the console.
    If CPU usage exceeds the specified threshold, a red alert is displayed.

    \b
    Examples:
      cli.py monitor
      cli.py monitor --threshold-cpu 90
    """
    if host != 'localhost':
        click.echo(f"Connecting to {host} for monitoring...")
        client = ssh_connect(host, 'admin')  # Use env vars for creds in prod
        stdin, stdout, stderr = client.exec_command('uptime && free -h && df -h')
        output = stdout.read().decode()
        client.close()
        click.echo(output)
    else:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        click.echo(f"[{datetime.now()}] CPU: {cpu}%, Mem: {mem}%, Disk: {disk}%")
        if cpu > threshold_cpu:
            click.echo("High CPU alert!")

#Log analyzer
@cli.command()
@click.argument('logfile', type=click.Path(exists=True))
@click.option('--errors-only', is_flag=True,
              help='Show only lines containing ERROR or FAIL keywords.')
def logs(logfile, errors_only):
    """
    Analyze a log file for recent entries or errors.

    This command reads the last 100 lines of the given log file and,
    if requested, filters only those lines containing error-related
    keywords like 'ERROR' or 'FAIL'.

    \b
    Examples:
      cli.py logs /var/log/syslog
      cli.py logs app.log --errors-only
    """
    with open(logfile, 'r') as f:
        lines = f.readlines()[-100:]  # Last 100 lines

    errors = [line for line in lines if 'ERROR' in line or 'FAIL' in line] if errors_only else lines
    click.echo(f"Recent log entries ({len(errors)} lines shown):")
    for line in errors:
        click.echo(line.strip())


if __name__ == '__main__':
    cli()
