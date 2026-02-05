# Local ML Inference

While the cloud backend handles heavy generative AI tasks (like the Chatbot and RAG), the **Desktop Agent** is responsible for **Edge Intelligence**.

The "Local ML Engine" is a lightweight, low-latency module designed to analyze system metrics in real-time, directly on the user's hardware. This ensures that critical alerts (like thermal runaway or crypto-mining malware) are detected immediately, even without an internet connection.

---

## 🧠 Why Local Inference?

Running Machine Learning models locally on the client provides three key advantages:

1.  **Zero Latency:** Decisions are made in milliseconds. There is no network round-trip time.
2.  **Privacy:** Sensitive raw telemetry does not need to leave the device for basic health checks.
3.  **Offline Protection:** The system continues to monitor and protect the device even when disconnected from the internet.

---

## ⚙️ The ML Pipeline

The local pipeline operates on a continuous loop, synchronized with the `psutil` metrics collector.

### 1. Preprocessing & Normalization
Raw data from `psutil` often varies in scale (e.g., CPU % is 0-100, while RAM bytes are in the billions).
* **Scaler:** Inputs are standardized using a pre-fitted `StandardScaler` (Z-score normalization) or MinMax scaling to ensure the neural network receives balanced inputs.
* **Windowing:** Data is not analyzed as single points but as **sliding windows** (e.g., the last 60 seconds of activity) to capture trends rather than noise.

### 2. Anomaly Detection Models
The agent utilizes lightweight unsupervised models to identify deviations from "normal" behavior.

* **Isolation Forest / One-Class SVM:** Used to detect outliers in multidimensional space (e.g., high CPU usage + low disk I/O + high network traffic = potential malware).
* **Statistical Thresholding:** Dynamic baselines are calculated for thermal sensors. If a temperature exceeds the moving average by $3\sigma$ (3 standard deviations), it is flagged.

### 3. Inference Engine
The actual execution uses highly optimized libraries to minimize CPU overhead.
* **Runtime:** `ONNX Runtime` or `Scikit-learn`.
* **Format:** Models are trained in the cloud and exported to `.onnx` or `.pkl` format, which the desktop agent downloads during updates.

---

## 🔄 Continuous Learning & Data Expansion

A core objective of the current project phase is **Neural Network Expansion**.

To build robust Deep Learning models (such as LSTMs for failure prediction), the system requires a massive, diverse dataset of "healthy" vs. "unhealthy" machine states.

### The Training Loop
1.  **Data Collection:** The desktop app runs continuously, logging labeled telemetry data.
2.  **Cloud Upload:** Anonymized feature vectors are sent to Supabase.
3.  **Centralized Training:** The backend uses this aggregate data to retrain and refine the neural networks.
4.  **Model Push:** Improved model weights are versioned and pushed back to the Desktop Agent.

> **Current Status:** The system is currently in an active **Data Accumulation Phase**, gathering high-fidelity metrics to train the next generation of predictive Neural Networks.

---

## 💻 Code Architecture

The ML Engine is decoupled from the UI to ensure the app stays responsive.

```python
class LocalMLEngine:
    def __init__(self, model_path):
        self.model = load_model(model_path)
        self.scaler = load_scaler(model_path)
        self.history_window = deque(maxlen=60) # Store last 60 seconds

    def analyze(self, raw_metrics):
        # 1. Preprocess
        vector = self._vectorize(raw_metrics)
        self.history_window.append(vector)
        
        # 2. Inference (if window full)
        if len(self.history_window) == 60:
            flattened_window = np.array(self.history_window).flatten()
            anomaly_score = self.model.decision_function([flattened_window])
            
            # 3. Decision
            if anomaly_score < -0.5:
                return AnomalyType.CRITICAL
        
        return AnomalyType.NORMAL
```

## 🔮 Future: Neural Networks
As the dataset grows, the Local ML Engine will transition from statistical models to deep neural networks:

Autoencoders: for superior unsupervised anomaly detection.

RNNs/LSTMs: for time-series forecasting (e.g., "Your CPU will overheat in 10 minutes").