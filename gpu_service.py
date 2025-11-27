import requests
import json
import time
from datetime import datetime
import subprocess


CLOUD_URL = "http://localhost:8081/report" # temporary for now
INTERVAL = 5

# collects the data from GPU
def get_gpu_metrics():
    result = subprocess.run(
        ["rocm-smi", "--showallinfo", "--json"],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout.strip())
    
    gpus = []
    for card, metrics in data.items():
        if not card.startswith("card"):
            continue
        gpus.append({
            "gpu_id": card,
            "name": metrics.get("Device Name"),
            "temperature_edge_c": float(metrics.get("Temperature (Sensor edge) (C)", 0)),
            "temperature_hotspot_c": float(metrics.get("Temperature (Sensor junction) (C)", 0)),
            "temperature_mem_c": float(metrics.get("Temperature (Sensor memory) (C)", 0)),
            "utilization_percent": int(metrics.get("GPU use (%)", 0)),
            "vram_percent": int(metrics.get("GPU Memory Allocated (VRAM%)", 0))
        })
    return gpus

if __name__ == "__main__":
    print("GPU service started, pushing to:", CLOUD_URL)

    while True:
        try:
            metrics = get_gpu_metrics()
            data = {
                "timestamp": datetime.now().isoformat(),
                "machine_id": "desktop",
                "gpus": metrics
            }                      
            response = requests.post(CLOUD_URL, json=data, timeout=5)
            print(f"Pushed {len(metrics)} GPUs - Status: {response.status_code}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(INTERVAL)