crafty-prom
===========

Prometheus Exporter for Crafty Controller server statistics.

## Setup

```
python3 -m pip install -r requirements.txt
cp config.example.yaml config.yaml
# ... edit config.yaml ...
python3 main.py
# metrics endpoint is bound to 0.0.0.0:9877
```

<details>
  <summary>Metrics endpoint output</summary>

```ini
# HELP crashed Server has crashed
# TYPE crashed gauge
crashed{server_id="e191c9c8-8d22-485c-b517-37f4e991aa3f"} 0.0
crashed{server_id="b5cb2946-ccca-4a80-b2fc-eb27a7ff40c2"} 0.0
# HELP cpu_usage Current CPU usage
# TYPE cpu_usage gauge
cpu_usage{server_id="e191c9c8-8d22-485c-b517-37f4e991aa3f"} 7.25
cpu_usage{server_id="b5cb2946-ccca-4a80-b2fc-eb27a7ff40c2"} 0.0
# HELP created_seconds_total Created seconds ago
# TYPE created_seconds_total counter
created_seconds_total{server_id="e191c9c8-8d22-485c-b517-37f4e991aa3f"} 510132.477375
created_seconds_total{server_id="b5cb2946-ccca-4a80-b2fc-eb27a7ff40c2"} 91487.065666
# HELP connection_info Connection data
# TYPE connection_info gauge
connection_info{description="38C3 Survival",hostname="s1.minny.io",server_id="e191c9c8-8d22-485c-b517-37f4e991aa3f",server_port="25568",server_type="minecraft-java",version="1.21.4",world_name="38C3 Survival"} 1.0
connection_info{description="A Minecraft Server",hostname="s2.minny.io",server_id="b5cb2946-ccca-4a80-b2fc-eb27a7ff40c2",server_port="25565",server_type="minecraft-java",version="Paper 1.21.4",world_name="38c3 Plugin"} 1.0
# HELP players_online Players online
# TYPE players_online gauge
players_online{server_id="e191c9c8-8d22-485c-b517-37f4e991aa3f"} 7.0
players_online{server_id="b5cb2946-ccca-4a80-b2fc-eb27a7ff40c2"} 0.0
# HELP players_max Max players count
# TYPE players_max gauge
players_max{server_id="e191c9c8-8d22-485c-b517-37f4e991aa3f"} 64.0
players_max{server_id="b5cb2946-ccca-4a80-b2fc-eb27a7ff40c2"} 20.0
# HELP memory_usage_mb Current memory usage in MB
# TYPE memory_usage_mb gauge
memory_usage_mb{server_id="e191c9c8-8d22-485c-b517-37f4e991aa3f"} 4800.0
memory_usage_mb{server_id="b5cb2946-ccca-4a80-b2fc-eb27a7ff40c2"} 1900.0
# HELP memory_percent Current memory usage percent
# TYPE memory_percent gauge
memory_percent{server_id="e191c9c8-8d22-485c-b517-37f4e991aa3f"} 31.0
memory_percent{server_id="b5cb2946-ccca-4a80-b2fc-eb27a7ff40c2"} 12.0
# HELP running Server is running
# TYPE running gauge
running{server_id="e191c9c8-8d22-485c-b517-37f4e991aa3f"} 1.0
running{server_id="b5cb2946-ccca-4a80-b2fc-eb27a7ff40c2"} 1.0
# HELP started_seconds_total Started seconds ago
# TYPE started_seconds_total counter
started_seconds_total{server_id="e191c9c8-8d22-485c-b517-37f4e991aa3f"} 101611.18148
started_seconds_total{server_id="b5cb2946-ccca-4a80-b2fc-eb27a7ff40c2"} 78869.181971
# HELP world_size_mb World size in MB
# TYPE world_size_mb gauge
world_size_mb{server_id="e191c9c8-8d22-485c-b517-37f4e991aa3f"} 1016.0
world_size_mb{server_id="b5cb2946-ccca-4a80-b2fc-eb27a7ff40c2"} 242.6
```
</details>

## Configuration Options

### Environment variables
       
| Environment variable     | Description                      | Default value  |
| ------------------------ | -------------------------------- | -------------- |
| EXPORTER_PORT            | Listen port for metrics exporter | `9877`         |
| CRAFTY_CONFIG            | Config file name                 | `config.yaml`  |
| LOGLEVEL                 | Python logging level             | `INFO`         |
| POLLING_INTERVAL_SECONDS | Crafty API polling interval      | `15` (seconds) |
| CRAFTY_API_TIMEOUT       | Crafty API request timeout       | `5` (seconds) |
