# GPU Performance Monitoring Infrastructure
## Overview
A complete GPU monitoring solution that collects real-time performance metrics from AMD Radeon hardware and visualizes them through a modern observability stack.
Built with Prometheus for metrics aggregation, Grafana for dashboards, and a custom Python service for hardware telemetry, all containerized with Docker and deployable
to AWS with using Terraform.

## Use Case: Live GPU Performance Benchmarks
The platform enables side-by-side comparison of GPU performance under real workloads. In this example, monitoring both the AMD RX 7800 XT and RX 7700 XT during a sustained stress test revealed:

- The 7800 XT delivered equivalent performance while maintaining 10-15% lower GPU utilization
- Improved thermal design kept the 7800 XT running 5-8°C cooler throughout the test
- Despite consuming ~15W more power, the 7800 XT achieved 20% better performance per watt

<img width="2446" height="1297" alt="image" src="https://github.com/user-attachments/assets/2ae7ebe5-19b8-4d5f-89e6-94363cefe597" />

## Use Case: Live Updates via Webhooks and Email
The Alertmanager is configured to monitor for multiple critical conditions (like high temperature, power spikes, or low utilization).
This specific example demonstrates the GPU Idle alert, where a notification is sent (email and webhook) when the GPU is free, allowing
external systems to automatically queue up new workloads.

<img width="2431" height="1155" alt="image" src="https://github.com/user-attachments/assets/07b0cff4-c0ba-4885-a9ce-1f1721a8d988" />

## Tech Stack
| Componenet | Technology | Functionality |
| :---        |     :---      |   :---        |
| **Metrics Exporter**   | Custom Python (`gpu_service.py`)     | Extracts raw GPU telemetry (ROCm SMI).    |
| **Metrics Endpoint** | Python (FastAPI/Uvicorn) | Acts as a central API/aggregator; exposes metrics on `/metrics` for Prometheus to scrape. |
| **Monitoring & Alerting** | Prometheus (v3.8.0) & Alertmanager (v0.29.0) | Handles time-series data storage, rule evaluation (`alert_rules.yml`), and email/webhook notifications. |
| **Visualization** | Grafana | Dashboards for real-time comparative analysis. |
| **Deployment** | Docker/Docker Compose | Defines the four-container stack and the isolated `gpu-observer_monitoring` network. |
| **Infrastructure** | AWS EC2 (t3.small) & Terraform | Managed infrastructure as code; automated SSH and secure port access. |

## System Architecture 
The core of the architecture is a Docker-defined pipeline where the GPU service pushes raw telemetry to the cloudservice (FastAPI),
which then exposes a Prometheus-compliant endpoint. Prometheus scrapes this data on the shared Docker network, and the results are visualized
in Grafana. Alerts are routed to Alertmanager, which handles notifications via authenticated SMTP and an event-driven webhook.
<img width="1678" height="713" alt="image" src="https://github.com/user-attachments/assets/93032f08-bddd-4cae-b3ce-44452bc2b49d" />



## Technical Highlights
- Automated Alerting Pipeline: Configured Alertmanager to reliably send email alerts via secure SMTP (Port 587) and simultaneously push real-time alerts to a webhook endpoint (/alert in cloud_service.py).
- Custom Metrics & Integration: Developed a Python service to integrate with ROCm SMI and expose metrics in a Prometheus format.
- Infrastructure as Code (IaC): Used Terraform to define and deploy the AWS EC2 instance, security group, and automated startup script, ensuring reproducible environments.
- Secure Credential Handling: Implemented a startup script to dynamically generate the final alertmanager.yml from a template using environment variables ($EMAIL_PASS) to prevent hardcoding secrets.
- Low-Latency Metrics Pipeline: Engineered a data collection system that scrapes critical GPU telemetry (utilization, temperature, power) at 5-second intervals, enabling genuine near-real-time hardware performance monitoring.





