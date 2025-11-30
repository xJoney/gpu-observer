import json
import os
from datetime import datetime
from fastapi import FastAPI, Response

# vars
LOG_DIR = "logs"
LATEST_METRICS = {}



# Log stuff
# puts entries into the log file
def log_json(entry):
    os.makedirs(LOG_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    logfile = os.path.join(LOG_DIR, f"metrics_{today}.log")
    with open(logfile, "a") as f:
        f.write(json.dumps(entry) + "\n")

# logs error message
def log_error(machine_id, err):
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": "error",
        "machine_id": machine_id,
        "error": err
    }
    log_json(entry)




# routes
app = FastAPI()
# receive report from gpu services
@app.post("/report")
def report(payload: dict):
    machine_id = "unknown"
    try:
        machine_id = payload.get("machine_id", "unknown")
        LATEST_METRICS[machine_id] = payload
        log_json(payload)
        print(f"Received metrics from {machine_id}")
        return {"status": "ok"}
    except Exception as e:
        log_error(machine_id, e)
        return {"status": "error", "message": str(e)}

# return latest metrics from all gpu services
@app.get("/summary")
def summary():
    if not LATEST_METRICS:
        return {"status": "no data"}
    return LATEST_METRICS

@app.get("/health")
def health():
    return {"status": "healthy", "machines": len(LATEST_METRICS)} # need to add check for the system health status

@app.get('/metrics')
def prom_metrics():
    lines = []

    for machine_id, data in LATEST_METRICS.items():
        gpus = data.get("gpus",[])

        for gpu in gpus:
            gpu_id = gpu.get("gpu_id", "unknown")
            labels = f'machine="{machine_id}",gpu="{gpu_id}",name="{gpu.get("name", "unknown")}"'  
            lines.append(f'gpu_temperature_edge{{{labels}}} {gpu.get("temperature_edge_c", 0)}')
            lines.append(f'gpu_temperature_hotspot{{{labels}}} {gpu.get("temperature_hotspot_c", 0)}')
            lines.append(f'gpu_temperature_memory{{{labels}}} {gpu.get("temperature_mem_c", 0)}')            
            lines.append(f'gpu_utilization_percent{{{labels}}} {gpu.get("utilization_percent", 0)}')
            lines.append(f'gpu_vram_percent{{{labels}}} {gpu.get("vram_percent", 0)}')
            lines.append(f'gpu_power_average{{{labels}}} {gpu.get("power_average",0)}')
            lines.append(f'gpu_power_max{{{labels}}} {gpu.get("power_max_w",0)}')
            lines.append(f'gpu_clock_gpu{{{labels}}} {gpu.get("clock_gpu",0)}')
            lines.append(f'gpu_clock_memory{{{labels}}} {gpu.get("clock_memory",0)}')

    return Response(content="\n".join(lines) + "\n", media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    print("cloud service on port 8081")
    uvicorn.run(app, host="0.0.0.0", port = 8081)


