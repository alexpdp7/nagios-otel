# About

This repository contains a library that helps setting up delivery of Nagios perfdata to OpenTelemetry collectors.

I am not familiar at all with OpenTelemetry, so probably this is all wrong.

# Usage

You must create a Python script that processes perfdata.
The [`examples` directory](examples) contains the script I am currently using.
The library defines a `nagios_otel.perfdata` module that parses Nagios perfdata, and a `nagios_otel.otel` module that implements exporting metrics to OpenTelemetry.
The script should use these functions to select the perfdata to process, and create the wanted metrics.

Then, edit the `/etc/nagios/nagios.cfg` file to configure Nagios to process perfdata:

```
process_performance_data=1
host_perfdata_file=/var/log/nagios/host-perfdata
host_perfdata_file_template=[HOSTPERFDATA]\t$TIMET$\t$HOSTNAME$\t$HOSTEXECUTIONTIME$\t$HOSTOUTPUT$\t$HOSTPERFDATA$
service_perfdata_file_template=[SERVICEPERFDATA]\t$TIMET$\t$HOSTNAME$\t$SERVICEDESC$\t$SERVICEEXECUTIONTIME$\t$SERVICELATENCY$\t$SERVICEOUTPUT$\t$SERVICEPERFDATA$
host_perfdata_file_mode=a
host_perfdata_file_processing_interval=60
host_perfdata_file_processing_command=process-host-perfdata-file
```

And create a `process-host-perfdata-file` command:

```
define command {
        command_line                   /opt/nagios-otel/venv/bin/python3 /opt/nagios-otel/examples/host_example.py <open-telemetry-collector-host> /var/log/nagios/host-perfdata
        command_name                   process-host-perfdata-file
}
```

In the example above:

* Clone this repo to the `/opt/nagios-otel` directory.
* Create a Python virtualenv in the `venv` subdirectory.
* Install this package to the virtualenv.

This example uses the [`host_example.py`](examples/host_example.py) script that only processes the `rta` metric from the `check_ping` monitoring plugin.
