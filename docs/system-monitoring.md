# System Monitoring

The desktop client collects real-time system metrics using `psutil`.

## Metrics Collected

- CPU usage (percentage & core-wise)
- RAM usage
- Disk usage and I/O
- System uptime
- Process snapshot

## Design Goals

- Lightweight
- Non-intrusive
- OS-agnostic abstraction