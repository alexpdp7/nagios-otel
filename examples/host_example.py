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
            perf_data = perfdata.parse_host_perfdata(line)
        except Exception as e:
            print(e)
            continue
        for metric in perf_data.perfdata:
            if metric.label == "rta":
                assert metric.uom == "ms"
                batcher.record_gauge(perf_data.timestamp, perf_data.host, "system.network.ping", int(metric.value * 1000), "ns")
                batcher.record_gauge(perf_data.timestamp, perf_data.host, "system.network.ping.warn", int(float(metric.warn) * 1000), "ns")
                batcher.record_gauge(perf_data.timestamp, perf_data.host, "system.network.ping.crit", int(float(metric.crit) * 1000), "ns")
    batcher.batch()
    file.unlink()
