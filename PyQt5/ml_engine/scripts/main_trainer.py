import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os
import sys
from pathlib import Path

# --- STEP 1: FIX IMPORTS ---
# Get the absolute path of the directory where this script lives (scripts/)
SCRIPT_DIR = Path(__file__).resolve().parent
# Get the parent directory (ml_engine/) and add it to sys.path
BASE_DIR = SCRIPT_DIR.parent
sys.path.append(str(SCRIPT_DIR))
sys.path.append(str(BASE_DIR))

# Now this works whether you run the script directly or from the PyQt app
try:
    from data_generators import (
        generate_cpu_mem_complex, 
        generate_disk_data, 
        generate_network_data
    )
except ImportError:
    # Fallback for specific package-style calls
    from ml_engine.scripts.data_generators import (
        generate_cpu_mem_complex, 
        generate_disk_data, 
        generate_network_data
    )

# Add temperature generator import (same fallback style)
try:
    from data_generators import generate_temperature_data
except ImportError:
    from ml_engine.scripts.data_generators import generate_temperature_data

# --- STEP 2: FIX DIRECTORY ERROR ---
# Define a robust path for models
MODEL_SAVE_PATH = BASE_DIR / "models"
MODEL_SAVE_PATH.mkdir(parents=True, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class MetricClassifier(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 2) # Binary: Normal (0) or Anomaly (1)
        )
    
    def forward(self, x):
        return self.net(x)

def train_and_save(model_name, input_dim, X_train, y_train,epoch_count =1000, show_every_epoch=50):
    model = MetricClassifier(input_dim).to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    
    X = torch.tensor(X_train, dtype=torch.float32).to(device)
    y = torch.tensor(y_train, dtype=torch.long).to(device)
    
    print(f"\n--- Training {model_name} Model ---")
    for epoch in range(epoch_count):
        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()
        if epoch % show_every_epoch == 0:
            print(f"Epoch {epoch} | Loss: {loss.item():.6f}")
            
    save_file = MODEL_SAVE_PATH / f"{model_name}.pth"
    torch.save(model.state_dict(), str(save_file))
    print(f"Model saved to: {save_file}")
    # Clean up GPU memory
    del X, y, model
    torch.cuda.empty_cache()

if __name__ == "__main__":
    # 1. DISK TRAINING
    d_norm, l_norm = generate_disk_data(1000, "normal")
    d_fill, l_fill = generate_disk_data(500, "filling")
    d_wipe, l_wipe = generate_disk_data(500, "wiping")
    X_disk = np.vstack((d_norm, d_fill, d_wipe))
    y_disk = np.hstack((l_norm, l_fill, l_wipe))
    train_and_save("disk_analyser", 1, X_disk, y_disk)

    # 2. NETWORK TRAINING
    n_norm, nl_norm = generate_network_data(1000, "normal")
    n_exf, nl_exf = generate_network_data(500, "exfiltration")
    X_net = np.vstack((n_norm, n_exf))
    y_net = np.hstack((nl_norm, nl_exf))
    train_and_save("network_analyser", 2, X_net, y_net)

    # 3. CPU/MEM COMPLEX TRAINING
    c_norm, cl_norm = generate_cpu_mem_complex(1000, "normal")
    c_crash, cl_crash = generate_cpu_mem_complex(500, "crash")
    X_cpu = np.vstack((c_norm, c_crash))
    y_cpu = np.hstack((cl_norm, cl_crash))
    train_and_save("cpu_mem_analyser", 3, X_cpu, y_cpu)

    # 4. TEMPERATURE TRAINING (new)
    t_norm, tl_norm = generate_temperature_data(1000, "normal")
    t_over, tl_over = generate_temperature_data(500, "overheat")
    t_spike, tl_spike = generate_temperature_data(500, "spike")
    X_temp = np.vstack((t_norm, t_over, t_spike))
    y_temp = np.hstack((tl_norm, tl_over, tl_spike))
    train_and_save("temp_analyser", 1, X_temp, y_temp,10000,1000)