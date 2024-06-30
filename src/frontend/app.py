from flask import Flask
from flask import render_template

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from jinja2.environment import Template

import functools

from src.api import BackendApi

# ### OTel
provider = TracerProvider()
# processor = BatchSpanProcessor(ConsoleSpanExporter())
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)

# ### Flask

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)


def instrument(func, name):
    """Instrument existing function with an OTel span"""

    def inner(*args, **kwargs):
        with tracer.start_as_current_span(name):
            return func(*args, **kwargs)

    return inner


Template.render = instrument(Template.render, "render")


@app.route("/")
def index():
    backend_api = BackendApi()
    todos = backend_api.list()
    return render_template("index.html", todos=todos)


@app.route("/error")
def route_error():
    return render_template("error.html"), 500


@app.route("/exception")
def route_exception():
    raise RuntimeError("Internal Server Error")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
