import dataclasses
import datetime
import re
import typing


# See https://www.monitoring-plugins.org/doc/guidelines.html


def parse_host_perfdata(s):
    r"""
    >>> parse_host_perfdata("[HOSTPERFDATA]\t1699561142\texample.com\t4.088\tPING OK - Packet loss = 0%, RTA = 0.09 ms\trta=0.085000ms;3000.000000;5000.000000;0.000000 pl=0%;80;100;0")
    HostPerfdata(timestamp=datetime.datetime(2023, 11, 9, 21, 19, 2), host='example.com', host_execution_time=4.088, status='PING OK - Packet loss = 0%, RTA = 0.09 ms', perfdata=[Metric(label='rta', value=0.085, min_=0.0, max_=None, warn='3000.000000', crit='5000.000000'), Metric(label='pl', value=0.0, min_=0.0, max_=None, warn='80', crit='100')])
    """
    tag, timestamp_str, host, host_execution_time_str, status, perfdata = s.split("\t")
    assert tag == "[HOSTPERFDATA]", f"unexpected tag {tag} in {s}, expected [HOSTPERFDATA]"
    timestamp = datetime.datetime.fromtimestamp(int(timestamp_str))
    host_execution_time = float(host_execution_time_str)
    metrics = parse_metrics(perfdata)
    return HostPerfdata(timestamp, host, host_execution_time, status, metrics)


def parse_metrics(perfdata):
    metrics = perfdata.split(" ")
    return [parse_metric(m) for m in metrics]


def parse_metric(metric_str):
    """
    >>> parse_metric("rta=0.085000ms;3000.000000;5000.000000;0.000000")
    Metric(label='rta', value=0.085, min_=0.0, max_=None, warn='3000.000000', crit='5000.000000')
    """
    label_value_uom, warn, crit, min_str, max_str = (metric_str.split(";") + [None]*4)[0:5]
    label, value_uom = label_value_uom.split("=")
    value_str, uom = re.fullmatch(r"(-?[0-9]+(?:\.[0-9]+)?)(.*)", value_uom).groups()
    value = float(value_str)
    return Metric(label, value, float(min_str) if min_str else None, float(max_str) if max_str else None, warn, crit)


@dataclasses.dataclass
class Metric:
    label: str
    value: float
    min_: float
    max_: float

    """Leaving unparsed because plugins might be buggy :("""
    warn: str
    """Leaving unparsed because plugins might be buggy :("""
    crit: str


@dataclasses.dataclass
class HostPerfdata:
    timestamp: datetime.datetime
    host: str
    host_execution_time: float
    status: str
    perfdata: typing.List[Metric]
