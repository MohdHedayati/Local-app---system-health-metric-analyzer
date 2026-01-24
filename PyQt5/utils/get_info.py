import psutil
import datetime
import platform
import time
import json
import os
import collections
from utils.constants import DATA_FILE

# =======================
# Configuration
# =======================
SAMPLE_INTERVAL_SECONDS = 10
AGGREGATE_EVERY_N_SAMPLES = 30   # 5 minutes
MAX_RAW_SAMPLES = 120            # ~20 mins of raw data
TOP_PROCESSES_AGG = 50
MAX_AGGREGATED_RECORDS = 500

# =======================
# Metric Functions (UNCHANGED)
# =======================

NUM_CORES = psutil.cpu_count(logical=True)

def normalize_temp(value):
    if value is None:
        return None
    # NVMe / hwmon millidegree case
    if value > 1000:
        return round(value / 1000.0, 2)
    return value


def get_cpu_usage():
    return psutil.cpu_percent(interval=None)

def get_cpu_freq():
    try:
        freq = psutil.cpu_freq()
        if freq:
            return {"current_mhz": freq.current, "min_mhz": freq.min, "max_mhz": freq.max}
    except Exception:
        pass
    return None

def get_memory_info():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "ram": {
            "total_gb": round(mem.total / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent": mem.percent
        },
        "swap": {
            "used_gb": round(swap.used / (1024**3), 2),
            "percent": swap.percent
        }
    }

def get_disk_info():
    disk = psutil.disk_usage(os.getcwd())
    return {
        "total_gb": round(disk.total / (1024**3), 2),
        "used_gb": round(disk.used / (1024**3), 2),
        "percent": disk.percent
    }

def get_network_info():
    net = psutil.net_io_counters()
    return {
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv
    }

def get_cpu_temps():
    if platform.system() == "Windows":
        return {"available": False, "reason": "windows"}

    if not hasattr(psutil, "sensors_temperatures"):
        return {"available": False, "reason": "unsupported"}

    temps = psutil.sensors_temperatures()
    if not temps:
        return {"available": False, "reason": "no_sensors"}

    sensors = {}
    for sensor_name, entries in temps.items():
        sensors[sensor_name] = []
        for e in entries:
            sensors[sensor_name].append({
                "current": normalize_temp(e.current),
                "max": normalize_temp(e.high)
            })

    return {
        "available": True,
        "sensors": sensors
    }


def get_processes_info():
    procs = []
    for p in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            cpu_raw = p.info["cpu_percent"]
            if cpu_raw is None:
                continue

            procs.append({
                "pid": p.info["pid"],
                "name": p.info["name"],
                "cpu_percent_raw": cpu_raw,
                "cpu_percent_norm": round(cpu_raw / NUM_CORES, 2),
                "memory_percent": p.info["memory_percent"]
            })
        except Exception:
            pass

    procs.sort(key=lambda x: x["cpu_percent_norm"], reverse=True)
    return procs[:100]


# =======================
# Aggregation Logic (REWORKED)
# =======================
def aggregate_samples(samples):
    cpu_vals = [s["cpu"]["usage"] for s in samples]
    mem_vals = [s["memory"]["ram"]["percent"] for s in samples]
    disk_vals = [s["disk"]["percent"] for s in samples]

    # --- Network deltas ---
    tx_vals = [s["network"]["bytes_sent"] for s in samples]
    rx_vals = [s["network"]["bytes_recv"] for s in samples]

    network_delta = {
        "tx_bytes": tx_vals[-1] - tx_vals[0],
        "rx_bytes": rx_vals[-1] - rx_vals[0]
    }

    # --- Temperature aggregation ---
    temp_curr = []
    temp_max = []
    per_sensor = {}

    for s in samples:
        temps = s["temps"]
        if temps.get("available"):
            for sensor, entries in temps["sensors"].items():
                per_sensor.setdefault(sensor, {"current": [], "max": []})
                for e in entries:
                    if e["current"] is not None:
                        temp_curr.append(e["current"])
                        per_sensor[sensor]["current"].append(e["current"])
                    if e["max"] is not None:
                        temp_max.append(e["max"])
                        per_sensor[sensor]["max"].append(e["max"])

    if temp_curr:
        temp_block = {
            "available": True,
            "avg_c": round(sum(temp_curr) / len(temp_curr), 2),
            "max_c": max(temp_max) if temp_max else None,
            "per_sensor": {
                k: {
                    "avg": round(sum(v["current"]) / len(v["current"]), 2) if v["current"] else None,
                    "max": max(v["max"]) if v["max"] else None
                }
                for k, v in per_sensor.items()
            }
        }
    else:
        temp_block = {"available": False}


    # --- Process aggregation ---
    proc_map = {}


    for s in samples:
        for p in s["processes"]:
            pid = p["pid"]
            if pid not in proc_map:
                proc_map[pid] = {
                    "name": p["name"],
                    "cpu": []
                }
            proc_map.setdefault(p["pid"], {
                "name": p["name"],
                "cpu": []
            })["cpu"].append(p["cpu_percent_norm"])
    
    top_procs = sorted(
        (
            {
                "pid": pid,
                "name": data["name"],
                "avg_cpu": round(sum(data["cpu"]) / len(data["cpu"]), 2)
            }
            for pid, data in proc_map.items()
        ),
        key=lambda x: x["avg_cpu"],
        reverse=True
    )[:TOP_PROCESSES_AGG]

    return {
        "window": {
            "start": samples[0]["ts"],
            "end": samples[-1]["ts"],
            "duration_sec": SAMPLE_INTERVAL_SECONDS * len(samples)
        },
        "cpu": {
            "avg": round(sum(cpu_vals) / len(cpu_vals), 2),
            "min": min(cpu_vals),
            "max": max(cpu_vals),
            "std": round((sum((x - sum(cpu_vals)/len(cpu_vals))**2 for x in cpu_vals) / len(cpu_vals))**0.5, 2)
        },
        "memory_avg_percent": round(sum(mem_vals) / len(mem_vals), 2),
        "disk_avg_percent": round(sum(disk_vals) / len(disk_vals), 2),
        "network_delta": network_delta,
        "temps": temp_block,
        "top_processes_avg_cpu": top_procs
    }

# =======================
# Main Loop
# =======================
def main():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    psutil.cpu_percent(interval=None)

    state = {
        "recent_samples": collections.deque(maxlen=MAX_RAW_SAMPLES),
        "aggregates": []
    }

    try:
        while True:
            sample = {
                "ts": datetime.datetime.now().isoformat(),
                "cpu": {
                    "usage": get_cpu_usage(),
                    "freq": get_cpu_freq()
                },
                "memory": get_memory_info(),
                "disk": get_disk_info(),
                "network": get_network_info(),
                "temps": get_cpu_temps(),
                "processes": get_processes_info()
            }

            state["recent_samples"].append(sample)

            if len(state["recent_samples"]) > 0 and  len(state["recent_samples"]) % AGGREGATE_EVERY_N_SAMPLES == 0:
                block = list(state["recent_samples"])[:AGGREGATE_EVERY_N_SAMPLES]
                state["aggregates"].append(aggregate_samples(block))

                if len(state["recent_samples"]) >= MAX_RAW_SAMPLES:
                    for _ in range(AGGREGATE_EVERY_N_SAMPLES):
                        state["recent_samples"].popleft()

                if len(state["aggregates"]) > MAX_AGGREGATED_RECORDS:
                    state["aggregates"] = state["aggregates"][-MAX_AGGREGATED_RECORDS:]

            payload = {
                "schema_version": "3.0",
                "machine": {
                    "hostname": platform.node(),
                    "os": platform.system(),
                    "arch": platform.machine(),
                    "boot_time": psutil.boot_time()
                },
                "data": {
                    "recent_samples": list(state["recent_samples"]),
                    "aggregates": state["aggregates"]
                }
            }

            with open(DATA_FILE, "w") as f:
                json.dump(payload, f, indent=2)

            time.sleep(SAMPLE_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
