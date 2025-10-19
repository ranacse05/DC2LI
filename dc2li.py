#!/usr/bin/env python3
"""
DCAdminCLI - A unified system diagnostic and monitoring CLI tool.
"""

import click
import paramiko
import socket
import psutil
from datetime import datetime


def ssh_connect(host, user, key_path=None, password=None, timeout=10):
    """
    Establish SSH connection to remote host.
    
    Args:
        host: Target hostname or IP address
        user: SSH username
        key_path: Path to SSH private key (optional)
        password: SSH password (optional)
        timeout: Connection timeout in seconds
    
    Returns:
        paramiko.SSHClient object or None if connection fails
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        if key_path:
            client.connect(host, username=user, key_filename=key_path, timeout=timeout)
        elif password:
            client.connect(host, username=user, password=password, timeout=timeout)
        else:
            client.connect(host, username=user, timeout=timeout)
        return client
    except Exception as e:
        click.echo(f"SSH connection failed: {e}")
        return None


def get_remote_stats(client):
    """
    Get system statistics from remote host via SSH.
    
    Args:
        client: Connected paramiko.SSHClient object
    
    Returns:
        Dictionary containing CPU, memory, and disk usage percentages
    """
    stats = {}
    
    try:
        # CPU usage
        stdin, stdout, stderr = client.exec_command(
            "grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage}'"
        )
        cpu_usage = stdout.read().decode().strip()
        stats['cpu'] = float(cpu_usage) if cpu_usage else 0
        
        # Memory usage
        stdin, stdout, stderr = client.exec_command(
            "free | grep Mem | awk '{print $3/$2 * 100.0}'"
        )
        mem_usage = stdout.read().decode().strip()
        stats['memory'] = float(mem_usage) if mem_usage else 0
        
        # Disk usage
        stdin, stdout, stderr = client.exec_command(
            "df / | tail -1 | awk '{print $5}' | sed 's/%//'"
        )
        disk_usage = stdout.read().decode().strip()
        stats['disk'] = float(disk_usage) if disk_usage else 0
        
    except Exception as e:
        click.echo(f"Error retrieving remote stats: {e}")
        stats = {'cpu': 0, 'memory': 0, 'disk': 0}
    
    return stats


def test_connectivity(host, port=22, timeout=5):
    """
    Test network connectivity to host and port.
    
    Args:
        host: Target hostname or IP address
        port: Target port number
        timeout: Connection timeout in seconds
    
    Returns:
        Boolean indicating if connection was successful
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def get_color_for_metric(value, threshold, warning_factor=0.7):
    """
    Determine color based on value and threshold.
    
    Args:
        value: Current metric value
        threshold: Alert threshold
        warning_factor: Percentage of threshold for warning level
    
    Returns:
        Color string ('red', 'yellow', or 'green')
    """
    if value > threshold:
        return 'red'
    elif value > threshold * warning_factor:
        return 'yellow'
    else:
        return 'green'


@click.group()
def cli():
    """A simple system diagnostic and monitoring CLI tool."""
    pass


@cli.command()
@click.argument('hosts', nargs=-1, type=str)
@click.option('--ports', default='22,80,443', 
              help='Comma-separated list of ports to scan (default: 22,80,443).')
def netcheck(hosts, ports):
    """
    Check network connectivity and port status for one or more hosts.
    
    Examples:
      dcli.py netcheck 8.8.8.8 example.com
      dcli.py netcheck localhost --ports 22,8080,3306
    """
    ports_list = [int(port) for port in ports.split(',')]
    target_hosts = hosts or ['8.8.8.8']
    
    for host in target_hosts:
        click.echo(f"Checking {host}...")
        
        # Test basic connectivity
        if test_connectivity(host, 22, 2):
            click.echo(click.style("Ping: OK", fg='green'))
        else:
            click.echo(click.style("Ping: FAILED", fg='red'))

        # Check specified ports
        for port in ports_list:
            if test_connectivity(host, port, 2):
                click.echo(click.style(f"  Port {port}: OPEN", fg='green'))
            else:
                click.echo(click.style(f"  Port {port}: CLOSED", fg='red'))
        
        click.echo()  # Add spacing between hosts


@cli.command()
@click.option('--host', default='localhost', help='Target host (IP or hostname)')
@click.option('--user', default='root', help='SSH username')
@click.option('--key-path', help='Path to SSH private key')
@click.option('--password', help='SSH password')
@click.option('--threshold-cpu', default=80, type=int, help='CPU alert threshold (%)')
@click.option('--threshold-mem', default=85, type=int, help='Memory alert threshold (%)')
@click.option('--threshold-disk', default=90, type=int, help='Disk alert threshold (%)')
@click.option('--timeout', default=10, type=int, help='SSH connection timeout (seconds)')
def monitor(host, user, key_path, password, threshold_cpu, threshold_mem, threshold_disk, timeout):
    """
    Monitor system resources (CPU, memory, disk) for local or remote host.
    
    Examples:
      dcli.py monitor
      dcli.py monitor --host 192.168.1.100 --user admin --password secret
    """
    if host != 'localhost':
        _monitor_remote(host, user, key_path, password, threshold_cpu, 
                       threshold_mem, threshold_disk, timeout)
    else:
        _monitor_local(threshold_cpu, threshold_mem, threshold_disk)


def _monitor_remote(host, user, key_path, password, threshold_cpu, 
                   threshold_mem, threshold_disk, timeout):
    """Monitor remote host system resources."""
    click.echo(f"Monitoring remote host: {host} as user '{user}'...")
    
    # Test connectivity first
    if not test_connectivity(host, 22, timeout):
        click.echo(f"Host {host} is not reachable on port 22")
        click.echo("Troubleshooting tips:")
        click.echo("  1. Check if the host is online")
        click.echo("  2. Verify SSH service is running")
        click.echo("  3. Check firewall settings")
        click.echo("  4. Verify network connectivity")
        return
    
    # Establish SSH connection
    client = ssh_connect(host, user, key_path, password, timeout)
    if not client:
        return
    
    try:
        # Get system statistics
        stats = get_remote_stats(client)
        
        # Display results
        _display_monitoring_results(stats, host, threshold_cpu, threshold_mem, threshold_disk)
        
    finally:
        client.close()


def _monitor_local(threshold_cpu, threshold_mem, threshold_disk):
    """Monitor local system resources."""
    # Get local system statistics
    stats = {
        'cpu': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent
    }
    
    _display_monitoring_results(stats, 'localhost', threshold_cpu, threshold_mem, threshold_disk)


def _display_monitoring_results(stats, host, threshold_cpu, threshold_mem, threshold_disk):
    """Display monitoring results with color coding and alerts."""
    # Display header
    click.echo(f"\n{click.style('System Statistics', bold=True)} - {host}")
    click.echo(f"Time: {datetime.now()}")
    
    # Display metrics with color coding
    cpu_color = get_color_for_metric(stats['cpu'], threshold_cpu)
    mem_color = get_color_for_metric(stats['memory'], threshold_mem)
    disk_color = get_color_for_metric(stats['disk'], threshold_disk)
    
    click.echo(click.style(f"CPU Usage:    {stats['cpu']:6.1f}%", fg=cpu_color))
    click.echo(click.style(f"Memory Usage: {stats['memory']:6.1f}%", fg=mem_color))
    click.echo(click.style(f"Disk Usage:   {stats['disk']:6.1f}%", fg=disk_color))
    
    # Check for alerts and warnings
    alerts, warnings = _check_thresholds(stats, threshold_cpu, threshold_mem, threshold_disk)
    
    # Display alerts and warnings
    if alerts:
        click.echo("\n" + click.style("CRITICAL ALERTS:", fg='red', bold=True))
        for alert in alerts:
            click.echo(click.style(f"  * {alert}", fg='red', bold=True))
    
    if warnings:
        click.echo("\n" + click.style("WARNINGS:", fg='yellow', bold=True))
        for warning in warnings:
            click.echo(click.style(f"  * {warning}", fg='yellow'))
    
    if not alerts and not warnings:
        click.echo(click.style("\nAll systems normal", fg='green', bold=True))


def _check_thresholds(stats, threshold_cpu, threshold_mem, threshold_disk):
    """Check metrics against thresholds and return alerts and warnings."""
    alerts = []
    warnings = []
    
    # Critical alerts
    if stats['cpu'] > threshold_cpu:
        alerts.append(f"High CPU usage: {stats['cpu']:.1f}%")
    if stats['memory'] > threshold_mem:
        alerts.append(f"High Memory usage: {stats['memory']:.1f}%")
    if stats['disk'] > threshold_disk:
        alerts.append(f"High Disk usage: {stats['disk']:.1f}%")
    
    # Warnings (approaching thresholds)
    warning_factor = 0.7
    if (threshold_cpu * warning_factor < stats['cpu'] <= threshold_cpu):
        warnings.append(f"CPU usage getting high: {stats['cpu']:.1f}%")
    if (threshold_mem * warning_factor < stats['memory'] <= threshold_mem):
        warnings.append(f"Memory usage getting high: {stats['memory']:.1f}%")
    if (threshold_disk * warning_factor < stats['disk'] <= threshold_disk):
        warnings.append(f"Disk usage getting high: {stats['disk']:.1f}%")
    
    return alerts, warnings


@cli.command()
@click.argument('logfile', type=click.Path(exists=True))
@click.option('--errors-only', is_flag=True,
              help='Show only lines containing ERROR or FAIL keywords.')
def logs(logfile, errors_only):
    """
    Analyze log file for recent entries or errors.
    
    Examples:
      dcli.py logs /var/log/syslog
      dcli.py logs app.log --errors-only
    """
    try:
        with open(logfile, 'r') as file:
            lines = file.readlines()[-100:]  # Last 100 lines
        
        if errors_only:
            filtered_lines = [
                line for line in lines 
                if any(keyword in line.upper() for keyword in ['ERROR', 'FAIL'])
            ]
        else:
            filtered_lines = lines
        
        click.echo(f"Recent log entries ({len(filtered_lines)} lines shown):")
        for line in filtered_lines:
            click.echo(line.rstrip())
            
    except Exception as e:
        click.echo(f"Error reading log file: {e}")


if __name__ == '__main__':
    cli()