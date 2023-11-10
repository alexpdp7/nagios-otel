import datetime

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.sdk.metrics.export import MetricsData, ResourceMetrics, ScopeMetrics, Metric, Sum, Gauge, Histogram, NumberDataPoint
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter as OTLPGRPCMetricExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter as OTLPHTTPMetricExporter


def foo(exporter):
    metric_datetime = datetime.datetime.now()
    resource_attributes = {"resource_attribute": "value"}
    resource = Resource(resource_attributes)
    instrumentation_scope_name = "instrumentation_scope_name"
    instrumentation_scope_version = "instrumentation_scope_version"
    scope = InstrumentationScope(instrumentation_scope_name, instrumentation_scope_version)
    metric_attributes = {"metric_attribute": "value"}
    time_unix_nano = int(metric_datetime.timestamp() * 10**9)
    metric_value = 3
    data_points = [NumberDataPoint(metric_attributes, None, time_unix_nano, metric_value)]
    metric_data = Gauge(data_points)
    metric_name = "metric_name"
    metric_description = "metric_description"
    metric_unit = ""
    metrics = [Metric(metric_name, metric_description, metric_unit, metric_data)]
    scope_metricss = [ScopeMetrics(scope, metrics, None)]
    resource_metricss = [ResourceMetrics(resource, scope_metricss, None)]
    metrics_data = MetricsData(resource_metricss)
    exporter.export(metrics_data)


def create_grpc_metric_exporter(host, insecure, port=4317):
    return OTLPGRPCMetricExporter(endpoint=f"{host}:{port}", insecure=insecure)


def create_http_metric_exporter(host, protocol="http", port=4318, endpoint="/v1/metrics"):
    return OTLPHTTPMetricExporter(endpoint=f"{protocol}://{host}:{port}{endpoint}")
