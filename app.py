"""Demo App using Flask"""

import requests
from flask import Flask, jsonify
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

# Initialize tracing and an exporter that can send data to an OTLP endpoint
resource = Resource(attributes={ResourceAttributes.SERVICE_NAME: "flask-demo-app"})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Create a tracer
tracer = trace.get_tracer(__name__)

app = Flask(__name__)

# Instrument Flask
FlaskInstrumentor().instrument_app(app)

# Instrument requests
RequestsInstrumentor().instrument()


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
