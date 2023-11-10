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


def parse_service_perfdata(s):
    r"""
    >>> parse_service_perfdata("[SERVICEPERFDATA]\t1699561212\texample.com\tcheck_ragent\t0.340\t0.000\tRAGENT OK\t'/_available_bytes'=3629514752B;858993459;429496729;0;4294967296 '/_available_inodes'=7089128;1424606;712303;0;7123032 '/var/lib/pgsql_available_bytes'=1673789440B;429496729;214748364;0;2147483648 '/var/lib/pgsql_available_inodes'=3269136;654367;327183;0;3271835 '/dev_available_bytes'=499712B;100761;50380;0;503808 '/dev_available_inodes'=16473766;3294757;1647378;0;16473788 '/dev/full_available_bytes'=67441057792B;2147483648;1073741824;0;67441057792 '/dev/full_available_inodes'=16464481;3293020;1646510;0;16465102 '/dev/null_available_bytes'=67441057792B;2147483648;1073741824;0;67441057792 '/dev/null_available_inodes'=16464481;3293020;1646510;0;16465102 '/dev/random_available_bytes'=67441057792B;2147483648;1073741824;0;67441057792 '/dev/random_available_inodes'=16464481;3293020;1646510;0;16465102 '/dev/tty_available_bytes'=67441057792B;2147483648;1073741824;0;67441057792 '/dev/tty_available_inodes'=16464481;3293020;1646510;0;16465102 '/dev/urandom_available_bytes'=67441057792B;2147483648;1073741824;0;67441057792 '/dev/urandom_available_inodes'=16464481;3293020;1646510;0;16465102 '/dev/zero_available_bytes'=67441057792B;2147483648;1073741824;0;67441057792 '/dev/zero_available_inodes'=16464481;3293020;1646510;0;16465102 '/proc/sys/kernel/random/boot_id_available_bytes'=499712B;100761;50380;0;503808 '/proc/sys/kernel/random/boot_id_available_inodes'=16473766;3294757;1647378;0;16473788 '/dev/shm_available_bytes'=67475558400B;2147483648;1073741824;0;67476635648 '/dev/shm_available_inodes'=16473785;3294757;1647378;0;16473788 '/run_available_bytes'=26973728768B;2147483648;1073741824;0;26990657536 '/run_available_inodes'=819008;163840;81920;0;819200 'entropy'=256;128;64;0;")
    ServicePerfdata(timestamp=datetime.datetime(2023, 11, 9, 21, 20, 12), host='example.com', service='check_ragent', service_execution_time=0.34, service_latency=0.0, status='RAGENT OK', perfdata=[Metric(label="'/_available_bytes'", value=3629514752.0, min_=0.0, max_=4294967296.0, warn='858993459', crit='429496729'), Metric(label="'/_available_inodes'", value=7089128.0, min_=0.0, max_=7123032.0, warn='1424606', crit='712303'), Metric(label="'/var/lib/pgsql_available_bytes'", value=1673789440.0, min_=0.0, max_=2147483648.0, warn='429496729', crit='214748364'), Metric(label="'/var/lib/pgsql_available_inodes'", value=3269136.0, min_=0.0, max_=3271835.0, warn='654367', crit='327183'), Metric(label="'/dev_available_bytes'", value=499712.0, min_=0.0, max_=503808.0, warn='100761', crit='50380'), Metric(label="'/dev_available_inodes'", value=16473766.0, min_=0.0, max_=16473788.0, warn='3294757', crit='1647378'), Metric(label="'/dev/full_available_bytes'", value=67441057792.0, min_=0.0, max_=67441057792.0, warn='2147483648', crit='1073741824'), Metric(label="'/dev/full_available_inodes'", value=16464481.0, min_=0.0, max_=16465102.0, warn='3293020', crit='1646510'), Metric(label="'/dev/null_available_bytes'", value=67441057792.0, min_=0.0, max_=67441057792.0, warn='2147483648', crit='1073741824'), Metric(label="'/dev/null_available_inodes'", value=16464481.0, min_=0.0, max_=16465102.0, warn='3293020', crit='1646510'), Metric(label="'/dev/random_available_bytes'", value=67441057792.0, min_=0.0, max_=67441057792.0, warn='2147483648', crit='1073741824'), Metric(label="'/dev/random_available_inodes'", value=16464481.0, min_=0.0, max_=16465102.0, warn='3293020', crit='1646510'), Metric(label="'/dev/tty_available_bytes'", value=67441057792.0, min_=0.0, max_=67441057792.0, warn='2147483648', crit='1073741824'), Metric(label="'/dev/tty_available_inodes'", value=16464481.0, min_=0.0, max_=16465102.0, warn='3293020', crit='1646510'), Metric(label="'/dev/urandom_available_bytes'", value=67441057792.0, min_=0.0, max_=67441057792.0, warn='2147483648', crit='1073741824'), Metric(label="'/dev/urandom_available_inodes'", value=16464481.0, min_=0.0, max_=16465102.0, warn='3293020', crit='1646510'), Metric(label="'/dev/zero_available_bytes'", value=67441057792.0, min_=0.0, max_=67441057792.0, warn='2147483648', crit='1073741824'), Metric(label="'/dev/zero_available_inodes'", value=16464481.0, min_=0.0, max_=16465102.0, warn='3293020', crit='1646510'), Metric(label="'/proc/sys/kernel/random/boot_id_available_bytes'", value=499712.0, min_=0.0, max_=503808.0, warn='100761', crit='50380'), Metric(label="'/proc/sys/kernel/random/boot_id_available_inodes'", value=16473766.0, min_=0.0, max_=16473788.0, warn='3294757', crit='1647378'), Metric(label="'/dev/shm_available_bytes'", value=67475558400.0, min_=0.0, max_=67476635648.0, warn='2147483648', crit='1073741824'), Metric(label="'/dev/shm_available_inodes'", value=16473785.0, min_=0.0, max_=16473788.0, warn='3294757', crit='1647378'), Metric(label="'/run_available_bytes'", value=26973728768.0, min_=0.0, max_=26990657536.0, warn='2147483648', crit='1073741824'), Metric(label="'/run_available_inodes'", value=819008.0, min_=0.0, max_=819200.0, warn='163840', crit='81920'), Metric(label="'entropy'", value=256.0, min_=0.0, max_=None, warn='128', crit='64')])
    """
    tag, timestamp_str, host, service, service_execution_time_str, service_latency_str, status, perfdata = s.split("\t")
    assert tag == "[SERVICEPERFDATA]", f"unexpected tag {tag} in {s}, expected [SERVICEPERFDATA]"
    timestamp = datetime.datetime.fromtimestamp(int(timestamp_str))
    service_execution_time = float(service_execution_time_str)
    service_latency = float(service_latency_str)
    metrics = parse_metrics(perfdata)
    return ServicePerfdata(timestamp, host, service, service_execution_time, service_latency, status, metrics)


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


@dataclasses.dataclass
class ServicePerfdata:
    timestamp: datetime.datetime
    host: str
    service: str
    service_execution_time: float
    service_latency: float
    status: str
    perfdata: typing.List[Metric]
