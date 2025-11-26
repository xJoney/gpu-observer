import subprocess
import json
import os
import time
import threading
import uvicorn
from datetime import datetime
from fastapi import FastAPI

# vars
NAME = "GPU Monitor"
LOG_DIR = "logs"
SUCCESS_INTERVAL = 5
ERROR_INTERVAL = 10
LATEST_METRICS = None

# main func that retrieves metrics
def get_gpu_metrics():

    # Run rocm-smi in JSON mode
    result = subprocess.run(
        ["rocm-smi", "--showallinfo", "--json"],
        capture_output=True,
        text=True
    )

    raw = result.stdout.strip()
    data = json.loads(raw)

    gpus = []

    # loop through each GPU and extract metrics
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


# Log stuff

# returns path to today's log file
def get_daily_logfile():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"service_{today}.log")  #

# puts entries into the log file
def log_json(entry):
    os.makedirs(LOG_DIR, exist_ok=True)
    logfile = get_daily_logfile()

    with open(logfile, "a") as f:
        f.write(json.dumps(entry) + "\n")

# log successfull metric collection
def log_metrics(gpus):
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": "metrics",
        "gpus": gpus
    }
    log_json(entry)

# logs error message
def log_error(err):
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": "error",
        "error": err
    }
    log_json(entry)


# prints banner
def print_banner(gpu_count):
    print("===================================")
    print(f"{NAME} starting...")
    print(f"Detected GPUs: {gpu_count}")
    print(f"Logging to: {get_daily_logfile()}")
    print(f"Success interval: {SUCCESS_INTERVAL}s | Error interval: {ERROR_INTERVAL}s")
    print("===================================\n")



def metrics_loop():
    global LATEST_METRICS

    while True:
        try:
            metrics = get_gpu_metrics()
            LATEST_METRICS = {
                "timestamp" : datetime.now().isoformat(),
                "gpus" : metrics
            }
            log_metrics(metrics)
            time.sleep(SUCCESS_INTERVAL)
            print(f"OK:", metrics)
        except Exception as e:
            err_msg = str(e)
            log_error(err_msg)
            time.sleep(ERROR_INTERVAL)
            print(f"ERROR: ", err_msg)


# route for metrics 
app = FastAPI()
@app.get("/metrics")
def get_metrics():
    if LATEST_METRICS is None:
        return {"status": "warming_up", "message": "missing populated data.."}
    return LATEST_METRICS


if __name__ == "__main__":
    # startup failure handler
    try:
        initial_metrics = get_gpu_metrics()
        gpu_count = len(initial_metrics)
        print_banner(gpu_count)
    except Exception as e:
        print("Startup Error:", e)
        gpu_count = 0
        print_banner(gpu_count)

    # thread is running metrics_loop until main process ends/shutdown
    thread = threading.Thread(target=metrics_loop, daemon=True)
    thread.start()

    # runs the server
    uvicorn.run("gpu_service:app", host="0.0.0.0", port = 8080)


