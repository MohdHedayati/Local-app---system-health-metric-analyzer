import onnxruntime as ort
import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import os

class SystemAnalyticEngine:
    def __init__(self, model_path_prefix="ml_engine/models/"):
        # Load ONNX sessions (Self-contained, no class definition needed)
        self.models = {
            "cpu_mem": self._load_onnx(f"{model_path_prefix}cpu_mem_analyser.onnx"),
            "disk": self._load_onnx(f"{model_path_prefix}disk_analyser.onnx"),
            "network": self._load_onnx(f"{model_path_prefix}network_analyser.onnx"),
            "temp": self._load_onnx(f"{model_path_prefix}temp_analyser.onnx")
        }
        self.base_threat_weight = 0.15

    def _load_onnx(self, path):
        try:
            if not os.path.exists(path): return None
            # Use CPU Execution Provider for Render compatibility
            return ort.InferenceSession(path, providers=['CPUExecutionProvider'])
        except Exception: return None

    def _run_inference(self, session, input_data):
        if session is None: return 0
        # Convert to float32 numpy array and add batch dimension
        feat = np.array([input_data], dtype=np.float32)
        inputs = {session.get_inputs()[0].name: feat}
        outputs = session.run(None, inputs)
        return int(np.argmax(outputs[0]))

    def analyze_packet(self, input_json):
        data = json.loads(input_json)
        recent = data["data"]["recent_samples"]
        aggregates = data.get("data", {}).get("aggregates", [])
        
        recent_anomalies = {"cpu": False, "net": False, "disk": False, "temp": False}
        total_threat_score = 0.0
        
        for sample in recent:
            # Prepare features as simple lists
            cpu_feat = [sample["cpu"]["usage"], sample["memory"]["ram"]["percent"], sample["cpu"]["freq"]["current_mhz"]]
            disk_feat = [sample["disk"]["percent"]]
            net_feat = [sample["network"]["bytes_sent"], sample["network"]["bytes_recv"]]

            # Inference using ONNX Runtime
            c_a = self._run_inference(self.models["cpu_mem"], cpu_feat)
            d_a = self._run_inference(self.models["disk"], disk_feat)
            n_a = self._run_inference(self.models["network"], net_feat)

            # Temperature Logic
            t_a = 0
            temps_block = sample.get("temps", {})
            if isinstance(temps_block, dict) and temps_block.get("available"):
                vals = [e["current"] for sensor in temps_block.get("sensors", {}).values() for e in sensor if e.get("current") is not None]
                if vals:
                    avg_t = sum(vals) / len(vals)
                    t_a = self._run_inference(self.models["temp"], [avg_t])

            if c_a: recent_anomalies["cpu"] = True
            if d_a: recent_anomalies["disk"] = True
            if n_a: recent_anomalies["net"] = True
            if t_a: recent_anomalies["temp"] = True
            
            total_threat_score += (c_a * 0.5) + (n_a * 0.5) + (d_a * 0.3) + (t_a * 0.4)
        
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

            # Temperature checks on aggregates if available
            temps_block = window.get("temps", {})
            if isinstance(temps_block, dict) and temps_block.get("available"):
                if temps_block.get("max_c") and temps_block.get("max_c") > 95:
                    agg_findings.append("Aggregate shows critical thermal peaks")
                    agg_threat_contribution += 12.0

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

        # Add peak active period summary (top processes + top aggregate window)
        summary["peak_active_period"] = self._compute_peak_active_period(recent, aggregates)
        
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
    
    def _compute_peak_active_period(self, recent_samples, aggregates):
        """
        Builds a ranked top-5 processes list by composite score and returns top aggregate window.
        Composite uses multipliers:
          cpu -> 0.2, memory -> 0.3, temperature -> 0.15 (if available), network -> 0.2
        """
        if not recent_samples:
            return {"top_processes": [], "top_aggregate": None}

        # Aggregate per-process stats across recent_samples
        proc_map = {}  # key: (pid, name)
        sample_temps_available = False

        for s in recent_samples:
            net_total = s["network"]["bytes_sent"] + s["network"]["bytes_recv"]
            temps_block = s.get("temps", {})
            temps_available = isinstance(temps_block, dict) and temps_block.get("available")
            if temps_available:
                sample_temps_available = True
                vals = []
                for sensor, entries in temps_block.get("sensors", {}).items():
                    for e in entries:
                        if e.get("current") is not None:
                            vals.append(e["current"])
                sample_avg_temp = (sum(vals) / len(vals)) if vals else None
            else:
                sample_avg_temp = None

            for p in s.get("processes", []):
                key = (p["pid"], p["name"])
                entry = proc_map.setdefault(key, {"pid": p["pid"], "name": p["name"], "cpu_vals": [], "mem_vals": [], "net_vals": [], "temp_vals": [], "count": 0})
                entry["cpu_vals"].append(p.get("cpu_percent_norm", 0))
                entry["mem_vals"].append(p.get("memory_percent", 0) or 0)
                entry["net_vals"].append(net_total)
                if sample_avg_temp is not None:
                    entry["temp_vals"].append(sample_avg_temp)
                entry["count"] += 1

        # Compute averages
        procs = []
        cpu_list = []
        mem_list = []
        net_list = []
        temp_list = []
        for k, v in proc_map.items():
            avg_cpu = float(np.mean(v["cpu_vals"])) if v["cpu_vals"] else 0.0
            avg_mem = float(np.mean(v["mem_vals"])) if v["mem_vals"] else 0.0
            avg_net = float(np.mean(v["net_vals"])) if v["net_vals"] else 0.0
            avg_temp = float(np.mean(v["temp_vals"])) if v["temp_vals"] else None
            procs.append({"pid": v["pid"], "name": v["name"], "avg_cpu": avg_cpu, "avg_mem": avg_mem, "avg_net": avg_net, "avg_temp": avg_temp})
            cpu_list.append(avg_cpu)
            mem_list.append(avg_mem)
            net_list.append(avg_net)
            if avg_temp is not None:
                temp_list.append(avg_temp)

        def percentile(value, arr):
            if not arr:
                return 0.0
            arr = list(arr)
            less_eq = sum(1 for a in arr if a <= value)
            return less_eq / len(arr)  # fraction 0..1

        top_candidates = []
        for p in procs:
            cpu_pct = percentile(p["avg_cpu"], cpu_list)
            mem_pct = percentile(p["avg_mem"], mem_list)
            net_pct = percentile(p["avg_net"], net_list)
            temp_pct = percentile(p["avg_temp"], temp_list) if (p.get("avg_temp") is not None and temp_list) else 0.0

            score = cpu_pct * 0.2 + mem_pct * 0.3 + net_pct * 0.2
            if sample_temps_available:
                score += temp_pct * 0.15

            top_candidates.append({
                "pid": p["pid"],
                "name": p["name"],
                "score": round(score, 4),
                "avg_cpu": round(p["avg_cpu"], 3),
                "avg_mem": round(p["avg_mem"], 3),
                "avg_net": int(p["avg_net"]),
                "avg_temp": round(p["avg_temp"], 2) if p["avg_temp"] is not None else None
            })

        top_candidates.sort(key=lambda x: x["score"], reverse=True)
        top5 = top_candidates[:5]

        # Top aggregate window by cpu average (if aggregates exist)
        top_aggregate = None
        if aggregates:
            top_aggregate = max(aggregates, key=lambda a: a.get("cpu", {}).get("avg", 0))

        return {"top_processes": top5, "top_aggregate": top_aggregate}
    
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
        # safe thresholds may not be set; use large default if missing
        if tx_bytes > getattr(self, "thresholds", {}).get('max_tx_per_interval', 10**8):
            agg_report["flags"].append("Massive outbound data transfer detected")
            agg_report["risk_increase"] += 45.0

        # 3. Thermal Monitoring
        temps = aggregate_data.get("temps", {})
        if isinstance(temps, dict) and temps.get("available") and temps.get("max_c") and temps.get("max_c") > getattr(self, "thresholds", {}).get('critical_temp', 95):
            agg_report["flags"].append("Critical thermal threshold exceeded")
            agg_report["risk_increase"] += 10.0

        # 4. Aggregated Process Persistence
        top_procs = aggregate_data.get("top_processes_avg_cpu", [])
        for proc in top_procs:
            if any(bad_name in proc['name'].lower() for bad_name in getattr(self, "blacklist", [])):
                agg_report["flags"].append(f"Malicious process persistent: {proc['name']}")
                agg_report["risk_increase"] += 50.0

        if agg_report["flags"]:
            agg_report["status"] = "anomalous"
            
        return agg_report