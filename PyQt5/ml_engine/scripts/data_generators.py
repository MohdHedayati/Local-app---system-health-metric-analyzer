import numpy as np
import random

# --- DISK ANOMALIES (Focus on % Change) ---
def generate_disk_data(n_samples=1000, anomaly_type="normal"):
    """
    Types: 
    - 'filling': Rapid increase (Ransomware or temp file bloat)
    - 'wiping': Rapid decrease (Malicious cleanup or uninstaller)
    """
    data = []
    labels = []
    current_pct = 50.0  # Start at 50%
    
    for _ in range(n_samples):
        if anomaly_type == "normal":
            change = np.random.normal(0, 0.01) # Negligible jitter
        elif anomaly_type == "filling":
            change = np.random.uniform(0.5, 2.0) # 0.5% to 2% increase per sample
        elif anomaly_type == "wiping":
            change = np.random.uniform(-2.0, -0.5) # 0.5% to 2% decrease
            
        current_pct = np.clip(current_pct + change, 0, 100)
        data.append([current_pct])
        labels.append(1 if anomaly_type != "normal" else 0)
    return data, labels

# --- NETWORK ANOMALIES (Asymmetry & Throughput) ---
def generate_network_data(n_samples=1000, anomaly_type="normal"):
    """
    Types:
    - 'exfiltration': High bytes_sent, Low bytes_recv (Stealing data)
    - 'heavy_dl': Low bytes_sent, High bytes_recv (Updates or big downloads)
    - 'stalled': bytes_sent/recv drop to near zero despite high CPU/Mem
    """
    data = []
    labels = []
    
    for _ in range(n_samples):
        if anomaly_type == "normal":
            sent, recv = np.random.randint(100, 5000), np.random.randint(500, 10000)
        elif anomaly_type == "exfiltration":
            sent, recv = np.random.randint(50000, 200000), np.random.randint(100, 1000)
        elif anomaly_type == "heavy_dl":
            sent, recv = np.random.randint(100, 2000), np.random.randint(100000, 500000)
        elif anomaly_type == "stalled":
            sent, recv = np.random.randint(0, 50), np.random.randint(0, 50)
            
        data.append([sent, recv])
        labels.append(1 if anomaly_type != "normal" else 0)
    return data, labels

# --- CPU & MEMORY (Crashes & Frequency Anomalies) ---
def generate_cpu_mem_complex(n_samples=1000, anomaly_type="normal"):
    """
    Types:
    - 'crash': Usage goes 80% -> 0.1% instantly
    - 'throttling': Usage 100%, Freq 800MHz (Thermal limit)
    """
    data = []
    labels = []
    
    for i in range(n_samples):
        if anomaly_type == "crash":
            # Usage drops to near zero
            cpu, mem, freq = 0.5, 5.0, 800
        elif anomaly_type == "throttling":
            # High usage, forced low frequency
            cpu, mem, freq = 99.9, 90.0, 800
        else: # Normal
            cpu, mem, freq = np.random.normal(20, 5), np.random.normal(30, 5), 3200
            
        data.append([cpu, mem, freq])
        labels.append(1 if anomaly_type != "normal" else 0)
    return data, labels

# --- TEMPERATURE DATA ---
def generate_temperature_data(n_samples=1000, anomaly_type="normal"):
    """
    Produces a single-feature temperature (average over sensors) per sample.
    Types:
    - 'normal' : temperatures 35-65C with small jitter
    - 'overheat' : sustained high temperatures 85-110C (thermal events)
    - 'spike' : sudden short spike to 90-100 then back
    """
    data = []
    labels = []
    base = 45.0
    for i in range(n_samples):
        if anomaly_type == "normal":
            val = np.clip(np.random.normal(base, 4.0), 20, 80)
        elif anomaly_type == "overheat":
            val = np.clip(np.random.normal(95, 6.0), 60, 120)
        elif anomaly_type == "spike":
            if i % 50 == 0:
                val = np.clip(np.random.uniform(90, 105), 60, 120)
            else:
                val = np.clip(np.random.normal(base, 4.0), 20, 80)
        else:
            val = np.clip(np.random.normal(base, 4.0), 20, 80)

        data.append([val])
        labels.append(1 if anomaly_type != "normal" else 0)

    return data, labels