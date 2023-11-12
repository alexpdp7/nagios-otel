import pathlib
import re
import sys

from nagios_otel import otel, perfdata


"""
If you send this data to ClickHouse using:

https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/clickhouseexporter

, you can simplify usage of the filesystem usage metrics with the following view:

CREATE VIEW mountpoint_usage AS
SELECT
    ResourceAttributes['host.name'] AS host,
    Attributes['system.filesystem.mountpoint'] AS mountpoint,
    TimeUnix,
    anyIf(Value, (Attributes['system.filesystem.state']) = 'free') AS free,
    anyIf(Value, (Attributes['system.filesystem.state']) = 'used') AS used,
    anyIf(Value, (Attributes['system.filesystem.state']) = 'free') + anyIf(Value, (Attributes['system.filesystem.state']) = 'used') AS total
FROM otel_metrics_gauge
WHERE MetricName = 'system.filesystem.usage'
GROUP BY
    ResourceAttributes['host.name'],
    Attributes['system.filesystem.mountpoint'],
    TimeUnix

, which makes creating queries such as:

SELECT
    host,
    mountpoint,
    first_value(free) AS free,
    first_value(used) AS used,
    first_value(total) AS total,
    free / total AS pct_free,
    first_value(TimeUnix) AS when
FROM otel.mountpoint_usage
GROUP BY
    host,
    mountpoint

simpler.
"""


if __name__ == "__main__":
    metric_exporter = otel.create_grpc_metric_exporter(sys.argv[1], True)
    batcher = otel.MetricBatcher(metric_exporter)

    file = pathlib.Path(sys.argv[2])
    for line in file.read_text().splitlines():
        print(line)
        try:
            perf_data = perfdata.parse_service_perfdata(line)
        except Exception as e:
            print(e)
            continue
        for metric in perf_data.perfdata:
            if metric.label == "'entropy'":
                batcher.record_gauge(perf_data.timestamp, perf_data.host, "system.entropy.available", int(metric.value), None)
                batcher.record_gauge(perf_data.timestamp, perf_data.host, "system.entropy.warn", int(metric.warn[3:]), None)
                batcher.record_gauge(perf_data.timestamp, perf_data.host, "system.entropy.crit", int(metric.crit[3:]), None)
                continue
            m = re.match("'(.+)_used_bytes'", metric.label)
            if m:
                fs = m.group(1)
                if fs.startswith("/proc") or fs.startswith("/dev") or fs.startswith("/run"):
                    continue
                batcher.record_gauge(perf_data.timestamp, perf_data.host, "system.filesystem.usage", int(metric.value), "By", {
                    "system.filesystem.mountpoint": fs,
                    "system.filesystem.state": "used",
                })
                batcher.record_gauge(perf_data.timestamp, perf_data.host, "system.filesystem.usage", int(metric.max_ - metric.value), "By", {
                    "system.filesystem.mountpoint": fs,
                    "system.filesystem.state": "free",
                })
    batcher.batch()
    file.unlink()
