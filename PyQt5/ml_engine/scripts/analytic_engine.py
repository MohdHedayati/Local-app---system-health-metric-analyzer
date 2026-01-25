import torch
import json
import numpy as np
from datetime import datetime, timedelta
# Assuming the MetricClassifier class from previous step is imported
from ml_engine.scripts.main_trainer import MetricClassifier 

from pathlib import Path

class SystemAnalyticEngine:
    def __init__(self, model_path_prefix="ml_engine/models/"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load the models
        self.models = {
            "cpu_mem": self._load_model(f"{model_path_prefix}cpu_mem_analyser.pth", 3),
            "disk": self._load_model(f"{model_path_prefix}disk_analyser.pth", 1),
            "network": self._load_model(f"{model_path_prefix}network_analyser.pth", 2)
        }
        
        # Suspicious process names (Low base score)
        self.sus_watch_list = ["xmrig", "miner", "mimikatz", "nc.exe", "powershell", "cmd.exe", "temp_gen"]
        self.base_threat_weight = 0.15

    def _load_model(self, path, input_dim):

        model = MetricClassifier(input_dim).to(self.device)
        model.load_state_dict(torch.load(path))
        model.eval()
        return model

    def analyze_packet(self, input_json):
        data = json.loads(input_json)
        recent = data["data"]["recent_samples"]
        aggregates = data.get("data", {}).get("aggregates", [])
        
        recent_anomalies = {"cpu": False, "net": False, "disk": False}
        total_threat_score = 0.0
        
        # 1. PROCESS RECENT SAMPLES (Point-in-time Detection)
        for sample in recent:
            cpu_feat = torch.tensor([sample["cpu"]["usage"], sample["memory"]["ram"]["percent"], sample["cpu"]["freq"]["current_mhz"]], dtype=torch.float32).to(self.device)
            disk_feat = torch.tensor([sample["disk"]["percent"]], dtype=torch.float32).to(self.device)
            net_feat = torch.tensor([sample["network"]["bytes_sent"], sample["network"]["bytes_recv"]], dtype=torch.float32).to(self.device)

            with torch.no_grad():
                c_a = torch.argmax(self.models["cpu_mem"](cpu_feat.unsqueeze(0))).item()
                d_a = torch.argmax(self.models["disk"](disk_feat.unsqueeze(0))).item()
                n_a = torch.argmax(self.models["network"](net_feat.unsqueeze(0))).item()

            # Track if we saw any anomaly in the recent burst
            if c_a: recent_anomalies["cpu"] = True
            if d_a: recent_anomalies["disk"] = True
            if n_a: recent_anomalies["net"] = True
            
            total_threat_score += (c_a * 0.5) + (n_a * 0.5) + (d_a * 0.3)

        # 2. PROCESS AGGREGATES (Long-term Trend Detection)
        agg_findings = []
        agg_threat_contribution = 0.0
        
        for window in aggregates:
            # Check for sustained high CPU with low variance (Cryptojacking signature)
            if window["cpu"]["avg"] > 85 and window["cpu"]["std"] < 5:
                msg = f"Sustained CPU load detected in window {window['window']['start']}"
                agg_findings.append(msg)
                agg_threat_contribution += 10.0
            
            # Check for abnormal network deltas
            if window["network_delta"]["tx_bytes"] > 10**8: # Example 100MB threshold
                agg_findings.append("High volume data egress in aggregate window")
                agg_threat_contribution += 15.0

        # Combine scores
        global_score = round(total_threat_score + agg_threat_contribution, 2)

        # 3. BUILD SEPARATED SUMMARY
        summary = {
            "status": "CRITICAL" if global_score > 50 else "WARNING" if global_score > 15 else "HEALTHY",
            "global_threat_index": global_score,
            "recent_analysis": {
                "anomalies_detected": recent_anomalies,
                "recent_sample_count": len(recent)
            },
            "aggregate_analysis": {
                "sustained_threats": agg_findings,
                "window_count": len(aggregates),
                "trend_impact_score": agg_threat_contribution
            },
            "forecast_projection": self._generate_forecast(recent[-1], global_score / 100)
        }
        
        return summary

    def _generate_forecast(self, last_sample, trend_factor):
        """Generates 15 synthetic samples following the schema."""
        forecast = []
        last_ts = datetime.fromisoformat(last_sample["ts"].replace("Z", "+00:00"))
        
        for i in range(1, 16):
            new_ts = (last_ts + timedelta(seconds=i)).isoformat()
            # Predict behavior: if trend is high, usage increases slightly
            predicted_cpu = np.clip(last_sample["cpu"]["usage"] + (trend_factor * i), 0, 100)
            
            # Follow schema strictly
            f_sample = {
                "ts": new_ts,
                "cpu": {"usage": round(predicted_cpu, 2), "freq": last_sample["cpu"]["freq"]},
                "memory": last_sample["memory"],
                "disk": last_sample["disk"],
                "network": {
                    "bytes_sent": int(last_sample["network"]["bytes_sent"] * (1 + (trend_factor * 0.1))),
                    "bytes_recv": int(last_sample["network"]["bytes_recv"] * (1 + (trend_factor * 0.05)))
                },
                "temps": last_sample["temps"],
                "processes": last_sample["processes"][:3] # Keep top 3 for synthetic brevity
            }
            forecast.append(f_sample)
        return forecast
    
    def process_aggregates(self, aggregate_data):
        """
        Analyzes summarized system metrics over the collection interval.
        Focuses on sustained patterns (e.g., mining, exfiltration).
        """
        agg_report = {
            "status": "nominal",
            "flags": [],
            "risk_increase": 0.0
        }

        # 1. CPU Stability Analysis
        cpu = aggregate_data.get("cpu", {})
        avg_cpu = cpu.get("avg", 0)
        std_cpu = cpu.get("std", 0)
        
        # High average + Low standard deviation = Constant, heavy workload (Cryptojacking)
        if avg_cpu > 80 and std_cpu < 5:
            agg_report["flags"].append("Sustained heavy CPU load (Possible Mining)")
            agg_report["risk_increase"] += 30.0

        # 2. Network Delta (Exfiltration Detection)
        net = aggregate_data.get("network_delta", {})
        tx_bytes = net.get("tx_bytes", 0)
        if tx_bytes > self.thresholds['max_tx_per_interval']:
            agg_report["flags"].append("Massive outbound data transfer detected")
            agg_report["risk_increase"] += 45.0

        # 3. Thermal Monitoring
        temps = aggregate_data.get("temps", {})
        if temps.get("max_c", 0) > self.thresholds['critical_temp']:
            agg_report["flags"].append("Critical thermal threshold exceeded")
            agg_report["risk_increase"] += 10.0

        # 4. Aggregated Process Persistence
        top_procs = aggregate_data.get("top_processes_avg_cpu", [])
        for proc in top_procs:
            if any(bad_name in proc['name'].lower() for bad_name in self.blacklist):
                agg_report["flags"].append(f"Malicious process persistent: {proc['name']}")
                agg_report["risk_increase"] += 50.0

        if agg_report["flags"]:
            agg_report["status"] = "anomalous"
            
        return agg_report