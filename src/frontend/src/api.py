from pydantic import BaseModel
from typing import List
import requests
import os

from opentelemetry import trace
from opentelemetry.trace import set_span_in_context

from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
import opentelemetry.instrumentation.requests

# "manually" instrument requests
opentelemetry.instrumentation.requests.RequestsInstrumentor().instrument()

tracer = trace.get_tracer(__name__)


class Todo(BaseModel):
    id: int
    text: str
    status: bool


def propagate_w3c_header(r, *args, **kwargs):
    ctx = set_span_in_context(trace.get_current_span())
    headers = {}
    W3CBaggagePropagator().inject(headers, ctx)
    TraceContextTextMapPropagator().inject(headers, ctx)
    print(headers)


class BackendApi:
    pass

    def __init__(self) -> None:
        self.session = requests.Session()
        self.url = os.environ["BACKEND_API_URL"]

    @tracer.start_as_current_span("list")
    def list(self) -> List[Todo]:
        response = self.session.get(f"{self.url}/api/v1/items")
        items = response.json()["items"]
        return [Todo(**item) for item in items]

    @tracer.start_as_current_span("create")
    def create(self, body):
        pass

    # PATCH eh
    @tracer.start_as_current_span("update")
    def update(self, id, body):
        pass

    @tracer.start_as_current_span("delete")
    def delete(self, id) -> None:
        pass
