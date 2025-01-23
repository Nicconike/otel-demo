"""Demo App using Flask, OpenTelemetry and Prometheus"""

import os
import requests
from flask import Flask, jsonify, request, Response
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter

# Read OTLP Endpoint from environment
OTLP_ENDPOINT = os.environ.get(
    "OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318"
)

# OpenTelemetry Setup
resource = Resource(attributes={ResourceAttributes.SERVICE_NAME: "flask-demo-app"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Flask App
app = Flask(__name__)

# Automatically instrument Flask
FlaskInstrumentor().instrument_app(app)

# Automatically instrument requests
RequestsInstrumentor().instrument()

# Prometheus Metrics Setup
REQUEST_COUNTER = Counter(
    "http_requests_total", "Total HTTP requests", ["endpoint", "method"]
)


@app.before_request
def before_request():
    """Before Request"""
    REQUEST_COUNTER.labels(endpoint=request.endpoint, method=request.method).inc()


@app.route("/metrics")
def metrics():
    """Get Prometheus Metrics"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


# Routes
@app.route("/")
def hello():
    """Test Function"""
    return "Hello, OpenTelemetry!"


@app.route("/api/users")
def get_users():
    """Make a API call to an external service"""
    with tracer.start_as_current_span("get_users"):
        try:
            response = requests.get(
                "https://jsonplaceholder.typicode.com/users", timeout=20
            )
            response.raise_for_status()
            users = response.json()
            simplified_users = [
                {"id": user["id"], "name": user["name"], "email": user["email"]}
                for user in users
            ]
            return jsonify({"users": simplified_users})
        except requests.RequestException as e:
            app.logger.error("Error fetching users: %s", str(e))
            return jsonify({"error": "Failed to fetch users"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
