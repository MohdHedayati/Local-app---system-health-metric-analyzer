# ML Encoders & Neural Networks

While **Generative AI** allows the system to *speak*, **Machine Learning (ML)** allows the system to *feel*.

The ML Encoders and Neural Networks form the **subconscious monitoring layer** of the platform. They run silently in the background, processing thousands of data points per second to answer two fundamental questions:
1.  *"Is the system behaving normally right now?"* (Anomaly Detection)
2.  *"Is the system about to crash?"* (Predictive Maintenance)

---

## 🏗 The Limitations of Standard Monitoring

Traditional monitoring tools rely on **Static Thresholds**:
* *If CPU > 90%, send alert.*
* *If Temp > 80°C, send alert.*

**The Problem:** These rules are too rigid.
* **False Positive:** A video render *should* use 100% CPU. That is not an anomaly; it is work.
* **False Negative:** A cryptojacking virus might throttle itself to 50% CPU to stay hidden. A static threshold of 90% will never catch it.

**The Solution:** Neural Networks that learn **Contextual Normality**.

---

## 🧠 Model Architecture: The Autoencoder

The core of our anomaly detection engine is an **Autoencoder Neural Network**.

### How It Works
An Autoencoder is an unsupervised learning model that learns to copy its input to its output.

1.  **Encoder:** Compresses the complex system state (CPU, RAM, Disk, Net) into a small "Latent Vector" (a summary).
2.  **Bottleneck:** A constrained layer that forces the network to learn only the most important features.
3.  **Decoder:** Attempts to reconstruct the original input from the summary.

> *[Figure: Diagram showing Input Data flowing through Encoder to Bottleneck, then expanding via Decoder to Output]*

### The Anomaly Detection Logic
* We train the model **only on healthy data**. It learns exactly what "Normal" looks like.
* When we feed it a **Virus** or **Crash** signature, it fails to reconstruct it accurately because it has never seen it before.
* **Reconstruction Error:** The difference between Input and Output.
    * **Low Error** = Normal Behavior.
    * **High Error** = Anomaly Detected.

---

## 📉 Time-Series Forecasting (LSTM)

While Autoencoders detect *current* problems, **Long Short-Term Memory (LSTM)** networks predict *future* problems.

System crashes rarely happen instantly; they usually leave a trail of clues:
* *Minute 1:* Memory usage creeps up 1%.
* *Minute 5:* Disk Swap usage increases.
* *Minute 10:* CPU temperature rises slightly.
* *Minute 15:* **Crash.**

We employ LSTMs to analyze the **temporal sequence** of data. By remembering the past 60 seconds of metrics, the model can predict the probability of a system freeze occurring in the next 5 minutes.

---

## 🔢 Feature Engineering & Encoders

Raw numbers are not enough. We preprocess data into **Features** to make them understandable for the Neural Network.

| Raw Metric | Engineered Feature | Why? |
| :--- | :--- | :--- |
| **CPU %** | `cpu_volatility` | High volatility (jagged usage) is different from sustained load. |
| **Disk Bytes** | `io_pressure_index` | Combines Read+Write speed with Queue Depth to measure bottlenecking. |
| **Time** | `cyclic_time_encoding` | Converting time (0-24h) into Sin/Cos waves so the model understands 23:59 is close to 00:01. |

---

## 🔄 The Training Cycle (Active Learning)

The project is currently in an **Active Data Accumulation Phase**.

1.  **Edge Collection:** The Desktop Agent collects high-resolution telemetry.
2.  **Cloud Storage:** Data is stored in Supabase.
3.  **Offline Training:** We batch-train PyTorch models on this historical data.
4.  **Deployment:** The trained model weights (`.onnx` files) are pushed back to the Desktop Agent to run locally.

This cycle allows the system to get smarter over time, learning the specific "personality" of the user's hardware.