import pathlib
import sys

from nagios_otel import otel, perfdata


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
                batcher.record_gauge(perf_data.timestamp, perf_data.host, "system.entropy.warn", int(metric.warn), None)
                batcher.record_gauge(perf_data.timestamp, perf_data.host, "system.entropy.crit", int(metric.crit), None)
    batcher.batch()
    file.unlink()
