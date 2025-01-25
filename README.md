# OpenTelemetry Implementation with Flask and Observability Stack
This project demonstrates a observability setup using OpenTelemetry with a Flask application integrated with Prometheus, Loki, Tempo and Grafana

## Components
- **Flask Application (app.py):** A simple web application instrumented with OpenTelemetry to generate traces and metrics. By default, Python application logs are sent to stdout, which we ship to Loki via Promtail
- **Dockerfile:** Defines how to build the Docker image for the Flask application
- **OpenTelemetry Collector:** Receives, processes and exports telemetry data from instrumented apps to:
    - Tempo (traces)
    - Prometheus (metrics)
    - Loki (logs)
- **Prometheus:** Time series database for storing and querying metrics. Configured to scrape:
    - The OpenTelemetry Collector’s Prometheus endpoint
    - The Flask app’s /metrics endpoint (if desired)
- **Loki:** Log aggregation system for storing and querying logs
- **Tempo:** Distributed tracing backend. Receives traces via OTLP and stores them locally
- **Grafana:** Visualization platform for metrics, logs and traces
    - Data sources are automatically provisioned (Prometheus, Loki, Tempo)
    - Dashboards can also be provisioned for an all-in-one view
- **Promtail:** Tails Docker container logs (including the Flask app). Adds labels (e.g. job="my-flask-app") and sends logs to Loki
- **`docker-compose.yml`:** Orchestrates all services:
    - Builds/runs the Flask app
    - Runs the OpenTelemetry Collector, Prometheus, Loki, Tempo, Grafana and Promtail
    - Sets up networks and volume mounts for configuration files and data persistence

## Project Structure (Example)
```
├── app.py
├── Dockerfile
├── docker-compose.yml
├── otel-collector-config.yml
├── prometheus.yml
├── loki-config.yml
├── tempo.yml
├── promtail-config.yml
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── datasources.yml
│       └── dashboards/
│           ├── dashboards.yml
│           └── observability-dashboard.json
└── requirements.txt
```

## Detailed Component Explanations
### Flask Application (app.py)
The Flask application is instrumented with OpenTelemetry to generate traces, metrics and logs. Key points:
- FlaskInstrumentor for automatic instrumentation of Flask routes
- RequestsInstrumentor for outbound HTTP call instrumentation
- Sends traces to the OpenTelemetry Collector via OTLP
- Exposes /metrics endpoint (through `prometheus_client`) for Prometheus
- Logs go to stdout, which Promtail tails and ships to Loki

### Dockerfile
The Dockerfile is used to build the Docker image for the Flask application. It specifies:
- The base image (Python 3.12 slim version)
- Sets working directory in the container
- Installs dependencies from `requirements.txt`
- Copies in `app.py` and runs `python app.py`

### OpenTelemetry Collector (otel-collector-config.yml)
The Collector is configured to:
- Receive data via OTLP (OpenTelemetry Protocol) over gRPC(`4317`) and HTTP (`4318`)
- Process data using batch and memory_limiter processors
- Export traces to Tempo, metrics to Prometheus and logs to Loki

Key configuration sections:
- receivers: Defines how the Collector receives data
- processors: Configures data processing (batching and memory limiting)
- exporters: Specifies where to send the processed data
- service: Defines the data pipelines (traces, metrics, logs)

### Prometheus (prometheus.yml)
Prometheus is configured to scrape metrics from:
- The OpenTelemetry Collector’s Prometheus endpoint on port `8889`
- Scrape the Flask app on port 5000/metrics if it is serving metrics directly
- Default scrape interval: 15s

### Loki (loki-config.yml)
Loki is set up for log storage and querying. The configuration:
- Disables authentication for simplicity (not recommended for production)
- Uses in-memory storage and local filesystem, suitable for development/demo
- Configures retention and chunk storage settings
- Key sections:
    - server (port `3100`)
    - ingester
    - schema_config
    - storage_config
    - limits_config for log retention

### Tempo (tempo.yml)
Tempo is configured as the distributed tracing backend:
- Receives traces via OTLP (port `4317` or `4318`)
- Local filesystem storage for easy dev usage
- Sets a 1-hour retention in the compactor config for trace data

### Promtail (promtail-config.yml)
- Tails Docker container logs from the Docker socket
- If the container name matches a certain regex, it sets job="my-flask-app"
- Sends logs to Loki at `http://loki:3100`

### Grafana
Grafana is set up to visualize data from Prometheus, Loki and Tempo.
- Configured via `docker-compose.yml` to mount:
    - `./grafana/provisioning:/etc/grafana/provisioning`
        - Where provisioning files for datasources/dashboards live
    - `./grafana-data:/var/lib/grafana`
        - Where Grafana stores its internal database (persisting dashboards created in UI, etc)
- Datasources automatically provisioned in `datasources.yml`:
    - Prometheus → `http://prometheus:9090`
    - Loki → `http://loki:3100`
    - Tempo → `http://tempo:3200`
- Dashboards automatically provisioned in `dashboards.yml`, e.g. `observability-dashboard.json` for a combined panel of metrics, logs and traces

### Docker Setup (docker-compose.yml)
The `docker-compose.yml` file orchestrates all services:
- Builds and runs the Flask application
- Runs the OpenTelemetry Collector, Prometheus, Loki, Tempo and Grafana
- Sets up the necessary network connections between services
- Mounts configuration files as volumes

## How to Run
1. Ensure Docker and Docker Compose are installed
2. Clone this repository
    `git clone git@github.com:Nicconike/otel-demo.git`
3. Navigate to the project directory
4. Ensure all files are in the correct locations
5. Run `docker-compose up -d --build` to build the Flask app image & start all services
6. Check if all containers are running with `docker-compose ps`. You should see containers for Flask app, OpenTelemetry Collector, Prometheus, Loki, Tempo, Grafana and Promtail
    - Container names might be listed like `otel-demo-app-1`, `otel-demo-promtail-1`, etc.

After all the containers are up and running it would look something like below
![Docker](https://github.com/Nicconike/otel-demo/blob/master/assets/docker_desktop.png)

## Testing the Setup
1. Access the Flask application at `http://localhost:5000` where you will see “Hello, OpenTelemetry!”
2. Generate some test data:
    1. Visit `http://localhost:5000/api/users` multiple times to trigger external API calls and generates telemetry
    2. This will generate traces, metrics and logs
3. Promtail will collect logs from the Flask container, check container logs to confirm it's pushing logs to Loki

## Observing the Application
1. Access Grafana:
    - Open `http://localhost:3000` in your web browser
    - Log in with the default credentials (usually admin/admin)
    - Most Likely you may have anonymous access enabled
2. Ready-Made Data Sources (Provisioned)
    - Prometheus: `http://prometheus:9090`
    - Loki: `http://loki:3100`
    - Tempo: `http://tempo:3200`
    Check Configuration → Data Sources to confirm all three are green
3. Dashboards:
    - If you provisioned a dashboard using `observability-dashboard.json`, go to Dashboards → Manage → the Observability folder
    - Open **Observability Overview** to see panels
        - Metrics from Prometheus `rate(http_requests_total[5m])`
        - Logs from Loki `{job="my-flask-app"}`
        - Trace panel from Tempo (if supported)
        ![Prometheus](https://github.com/Nicconike/otel-demo/blob/master/assets/prometheus.png)

Dashboard (Incomplete)
![Dashboard](https://github.com/Nicconike/otel-demo/blob/master/assets/dashboard.png)
4. Explore Mode
    - **Metrics:** Explore with Prometheus. Example query:
    `rate(http_requests_total[1m])`
    ![Prometheus Metrics](https://github.com/Nicconike/otel-demo/blob/master/assets/metrics.png)
    - **Logs:** Explore with Loki. Example query:
    `{job="my-flask-app"}`
    ![Logs](https://github.com/Nicconike/otel-demo/blob/master/assets/container_logs.png)
    - **Traces:** Explore with Tempo. Filter by the service name defined in `app.py` (flask-demo-app)

## Persistent Data and Dashboards
- **Promtail** config is purely in `promtail-config.yml`
- **Grafana** data (e.g., if you edit dashboards in the UI) is stored in `./grafana-data:/var/lib/grafana`
- **Provisioned Dashboards** are the JSON files in `grafana/provisioning/dashboards/`
    - This ensures a baseline dashboard is always created on container startup
    - If you want to maintain the dashboards purely in code, re-export any changes from Grafana UI back into JSON

> [!NOTE]
> - This setup is designed for development and demonstration purposes only
> - Promtail is used to tail Docker logs and push them to Loki with labels
> - OpenTelemetry handles traces and metrics for the Python based Flask app
> - Grafana unifies views of logs, metrics and traces
> - For production use, enable proper authentication and adjust retention settings
> - Customize the Flask app and OpenTelemetry instrumentation as needed for your specific use case
