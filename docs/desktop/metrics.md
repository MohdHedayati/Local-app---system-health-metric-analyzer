# System Metrics Engine (psutil)

The core telemetry engine of the Desktop Agent is built upon **`psutil` (process and system utilities)**. This cross-platform library allows the application to retrieve information on running processes and system utilization (CPU, memory, disks, network, sensors) in a portable way.

This engine is responsible for the continuous high-frequency logging required to train the project's Neural Network models.

---

## 📊 Collected Metrics

To build a comprehensive health profile of the device, the agent collects data across five key subsystems:

### 1. CPU Telemetry
We monitor not just usage, but frequency and context switches to detect "silent" load.
* **Utilization:** Per-core and aggregate percentage.
* **Frequency:** Current, Minimum, and Maximum (Mhz).
* **Stats:** Context switches, interrupts, and syscalls.

### 2. Memory (RAM & Swap)
Tracking memory pressure helps predict system freezes before they happen.
* **Virtual Memory:** Total, Available, Used, Free.
* **Swap Memory:** Used, Free, Percent (critical for detecting thrashing).

### 3. Disk Subsystem
* **Usage:** Partition usage (Total/Used/Free).
* **I/O Counters:** Read count, Write count, Read bytes, Write bytes (essential for detecting ransomware-like behavior).

### 4. Network Traffic
* **Bytes:** Sent/Received.
* **Packets:** Sent/Received.
* **Errors:** Drop counts (indicates hardware or driver issues).

### 5. Hardware Sensors
* **Temperatures:** CPU and GPU thermal zones (critical for thermal throttling detection).
* **Battery:** Percentage, status (charging/discharging), and time remaining.

!!! warning "Platform Differences"
    Hardware sensors behave differently across OS versions. On **Windows**, administrative privileges are often required to read specific thermal zones, whereas **Linux** exposes them more freely via `/sys/class/thermal`. The engine handles these discrepancies gracefully using `try/except` blocks.

---

## 💻 Implementation Details

The collection logic runs on a dedicated background `QThread` to prevent freezing the GUI.

### Sample Collection Code

```python
import psutil
import time

def collect_snapshot():
    return {
        "timestamp": time.time(),
        "cpu": {
            "percent": psutil.cpu_percent(interval=None),
            "freq": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            "cores": psutil.cpu_count(logical=False)
        },
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        },
        "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
        "net_io": psutil.net_io_counters()._asdict()
    }
```

## 📦 Data Payload Structure
To facilitate Machine Learning training, data is normalized into a strictly typed JSON structure before being sent to Supabase. This consistency is vital for the ML expansion phase.

Example Payload sent to Cloud:

```JSON
{
  "device_id": "hw-uuid-550e-8400",
  "session_id": "sess-8892-xxy",
  "timestamp": "2023-10-27T10:00:00Z",
  "metrics": {
    "cpu_load": 12.5,
    "cpu_temp": 45.0,
    "ram_usage_percent": 64.2,
    "disk_read_mb": 120.5,
    "disk_write_mb": 45.2,
    "net_sent_mb": 1.2,
    "net_recv_mb": 5.8
  },
  "flags": {
    "is_throttling": false,
    "on_battery": true
  }
}
```

## 🧠 Role in Machine Learning
This module is not just for display; it is a Data Ingestion Pipeline.

By running continuously, the app accumulates a time-series dataset of "normal" vs. "abnormal" system behavior. This historical data is currently being aggregated in Supabase to train:

Anomaly Detection Autoencoders: To flag unusual spikes in resource usage.

Predictive LSTM Networks: To forecast system crashes based on rising thermal and memory trends.