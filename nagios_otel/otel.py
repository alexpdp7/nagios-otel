import dataclasses
import datetime

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.sdk.metrics.export import MetricsData, ResourceMetrics, ScopeMetrics, Metric, Sum, Gauge, Histogram, NumberDataPoint
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter as OTLPGRPCMetricExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter as OTLPHTTPMetricExporter


def create_grpc_metric_exporter(host, insecure, port=4317):
    return OTLPGRPCMetricExporter(endpoint=f"{host}:{port}", insecure=insecure)


def create_http_metric_exporter(host, protocol="http", port=4318, endpoint="/v1/metrics"):
    return OTLPHTTPMetricExporter(endpoint=f"{protocol}://{host}:{port}{endpoint}")


class MetricBatcher:
    def __init__(self, exporter):
        self.exporter = exporter
        self.resource_metric_to_datapoints = dict()

    def record_gauge(self, timestamp: datetime.datetime, host: str, metric: str, value: int, unit: str):
        resource = Resource({"host.name": host})
        metric_name = metric
        resource_metric = ResourceMetric(resource, metric_name, unit)
        if resource_metric not in self.resource_metric_to_datapoints:
            self.resource_metric_to_datapoints[resource_metric] = []
        self.resource_metric_to_datapoints[resource_metric].append(NumberDataPoint(None, None, int(timestamp.timestamp() * 10**9), value))

    def batch(self):
        instrumentation_scope = InstrumentationScope("nagios_otel", "0")
        for resource_metric, datapoints in self.resource_metric_to_datapoints.items():
            resource = resource_metric.resource
            metric = resource_metric.metric_name
            unit = resource_metric.unit
            metric_data = Gauge(datapoints)
            metrics = [Metric(metric, None, unit, metric_data)]
            scope_metricss = [ScopeMetrics(instrumentation_scope, metrics, None)]
            resource_metricss = [ResourceMetrics(resource, scope_metricss, None)]
            metrics_data = MetricsData(resource_metricss)
            self.exporter.export(metrics_data)


@dataclasses.dataclass(frozen=True)
class ResourceMetric:
    resource: Resource
    metric_name: str
    unit: str
