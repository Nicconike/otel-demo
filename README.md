# OpenTelemetry Implementation with Flask and Observability Stack
This project demonstrates a observability setup using OpenTelemetry with a Flask application integrated with Prometheus, Loki, Tempo and Grafana.

## Components
- **Flask Application (app.py):** A simple web application instrumented with OpenTelemetry
- **Dockerfile:** Defines how to build the Docker image for the Flask application
- **OpenTelemetry Collector:** Receives, processes and exports telemetry data
- **Prometheus:** Time series database for storing and querying metrics
- **Loki:** Log aggregation system
- **Tempo:** Distributed tracing backend
- **Grafana:** Visualization platform for metrics, logs and traces

## Detailed Component Explanations
### Flask Application (app.py)
The Flask application is instrumented with OpenTelemetry to generate traces, metrics and logs. Key points:
- Uses FlaskInstrumentor for automatic instrumentation of Flask
- Implements a custom /api/users endpoint that makes an external API call
- Configures OpenTelemetry to send data to the OpenTelemetry Collector

### Dockerfile
The Dockerfile is used to build the Docker image for our Flask application. It specifies:
- The base image (Python 3.12 slim version)
- The working directory in the container
- Install dependencies
- Copy the application code
- Command to run the application

### OpenTelemetry Collector (otel-collector-config.yml)
The Collector is configured to:
- Receive data via OTLP (OpenTelemetry Protocol) over gRPC and HTTP
- Process data using batch and memory_limiter processors
- Export traces to Tempo, metrics to Prometheus and logs to Loki

Key configuration sections:
- receivers: Defines how the Collector receives data
- processors: Configures data processing (batching and memory limiting)
- exporters: Specifies where to send the processed data
- service: Defines the data pipelines (traces, metrics, logs)

### Prometheus (prometheus.yml)
Prometheus is configured to scrape metrics from:
- The OpenTelemetry Collector
- Flask application (if it exposes metrics)
The configuration sets the scrape interval to 15 seconds

### Loki (loki-config.yml)
Loki is set up for log storage and querying. The configuration:
- Disables authentication for simplicity (not recommended for production)
- Uses in-memory storage and local filesystem, suitable for development/demo
- Configures retention and chunk storage settings

### Tempo (tempo.yml)
Tempo is configured as the distributed tracing backend:
- Receives traces via OTLP over gRPC
- Uses local storage for trace data
- Sets a 1-hour retention period for trace data

### Grafana
Grafana is set up to visualize data from Prometheus, Loki and Tempo. It's configured with:
- Anonymous access enabled (for demo purposes)
- Pre-configured data sources for Prometheus, Loki and Tempo

### Docker Setup (docker-compose.yml)
The docker-compose.yml file orchestrates all services:
- Builds and runs the Flask application
- Runs the OpenTelemetry Collector, Prometheus, Loki, Tempo and Grafana
- Sets up the necessary network connections between services
- Mounts configuration files as volumes

## How to Run
1. Ensure Docker and Docker Compose are installed
2. Clone this repository
3. Navigate to the project directory
4. Ensure all files are in the correct locations
5. Run `docker-compose up -d` to build the Flask app image & start all services
6. Check if all containers are running with `docker-compose ps`. You should see containers for Flask app, OpenTelemetry Collector, Prometheus, Loki, Tempo and Grafana

After all the containers are up and running it would look something like below
![Docker](https://github.com/Nicconike/otel-demo/blob/master/assets/docker_desktop.png)

## Testing the Setup
1. Access the Flask application at http://localhost:5000 where the homepage can be seen
2. Generate some test data:
    1. Visit http://localhost:5000/api/users multiple times to trigger API calls
    2. This will generate traces, metrics and logs

## Observing the Application
1. Access Grafana:
    - Open http://localhost:3000 in your web browser
    - Log in with the default credentials (usually admin/admin)
2. Configure data sources in Grafana (if not auto-configured):
    - Go to Configuration > Data Sources
    - Add Prometheus: http://prometheus:9090
    - Add Loki: http://loki:3100
    - Add Tempo: http://tempo:3200
3. Create Dashboards:
    - Metrics Dashboard:
        - Create a new dashboard
        - Add a panel with Prometheus as the data source
        - Query example: `rate(http_requests_total[5m])`
        ![Prometheus](https://github.com/Nicconike/otel-demo/blob/master/assets/prometheus.png)
    - Logs Dashboard:
        - Create a new dashboard
        - Add a logs panel with Loki as the data source
        - Query example: `{job="flask-app"}`
    - Traces View:
        - Use the Explore view in Grafana
        - Select Tempo as the data source
        - Search for traces by service name or duration
    Dashboard (Incomplete)
    ![Dashboard](https://github.com/Nicconike/otel-demo/blob/master/assets/dashboard.png)
4. Analyze the data:
    - Look for patterns in request rates and response times
    - Investigate any error logs
    - Examine trace spans to understand request flow and identify bottlenecks
5. Test alerting (optional):
    - Set up an alert rule in Grafana based on a metric
    - Trigger the alert condition and verify the alert fires

> [!NOTE]
> - This setup is designed for development and demonstration purposes
> - For production use, enable proper authentication and adjust retention settings
> - Customize the Flask app and OpenTelemetry instrumentation as needed for your specific use case
