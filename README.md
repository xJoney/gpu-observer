# GPU Performance Monitoring Infrastructure
## Overview
Built a containerized observability stack using Prometheus and Grafana to collect and 
analyze real-time performance metrics from AMD GPUs. Demonstrated infrastructure 
capabilities through comparative analysis of RX 7800 XT vs 7700 XT under sustained 
compute workloads.

## Tech Stack
- **Observability Platform**: Grafana + Prometheus (containerized with Docker)
- **Metrics Exporter**: Custom Python service integrating ROCm SMI (rocm-smi)
- **Data Collection**: Time-series metrics at 5s intervals
- **GPU Interface**: AMD RDNA3 GPUs via ROCm system management interface
- **Infrastructure**: Local development, AWS EC2 deployment planned

## Technical Highlights
- Custom metrics exporter development (Python + Prometheus client)
- Real-time monitoring dashboard design (Grafana)
- Time-series data collection and visualization
- Containerized observability stack deployment
- Hardware performance analysis and reporting

## Use Case: GPU Performance Comparison
Applied the monitoring infrastructure to compare AMD RX 7800 XT and 7700 XT under stress test workload:
- **Performance Efficiency**: 7800 XT achieved 10-15% lower utilization
- **Thermal Management**: 7800 XT maintained 5-8°C lower temperatures  
- **Power Efficiency**: 20% better performance/watt despite ~15W higher draw

<img width="2446" height="1297" alt="image" src="https://github.com/user-attachments/assets/2ae7ebe5-19b8-4d5f-89e6-94363cefe597" />



