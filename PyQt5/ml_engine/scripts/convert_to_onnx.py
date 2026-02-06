import torch
import torch.nn as nn
from pathlib import Path

# --- SETUP PATHS ---
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
MODEL_PATH = BASE_DIR / "models"

class MetricClassifier(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 2) 
        )
    
    def forward(self, x):
        return self.net(x)

def convert_model(model_name, input_dim):
    pth_file = MODEL_PATH / f"{model_name}.pth"
    onnx_file = MODEL_PATH / f"{model_name}.onnx"

    if not pth_file.exists():
        print(f"Skipping {model_name}: .pth file not found.")
        return

    model = MetricClassifier(input_dim)
    # Weights loaded on CPU for the export process
    model.load_state_dict(torch.load(str(pth_file), map_location=torch.device('cpu')))
    model.eval()

    dummy_input = torch.randn(1, input_dim)

    # --- THE FIX ---
    try:
        torch.onnx.export(
            model,
            dummy_input,
            str(onnx_file),
            export_params=True,
            # Opset 17 avoids the "No Adapter" error and is widely supported
            opset_version=17, 
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            # Keeping dynamic_axes for compatibility with standard inference engines
            dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
        )
        print(f"✅ Successfully converted: {model_name}.onnx")
    except Exception as e:
        print(f"❌ Failed to convert {model_name}: {e}")

if __name__ == "__main__":
    models_to_convert = [
        ("disk_analyser", 1),
        ("network_analyser", 2),
        ("cpu_mem_analyser", 3),
        ("temp_analyser", 1)
    ]

    for name, dim in models_to_convert:
        convert_model(name, dim)