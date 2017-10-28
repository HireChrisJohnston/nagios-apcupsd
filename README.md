# nagios-apcupsd
Nagios plugin for APC UPS software apcupsd to query for status and chart performance graphs with near instant updates (with some tweeks of Nagios settings).

## Design

* check_apcaccess.py is used to check a APC UPS using the apcaccess client utility.
* NRPD for passive check to notify of power loss or gain based on the apcups configuration
* NRPE for active checks at regular intervals under 'normal' conditions [and other types of checks](https://github.com/HireChrisJohnston/nagios-plugins)
* * [etc/apcupsd/onbattery](etc/apcupsd/onbattery)
* * [etc/apcupsd/offbattery](etc/apcupsd/offbattery) 

For fast response at the expense of a higher Nagios server load when using passive checks
~~~
      check_result_reaper_frequency=1
~~~
Other settings such as refresh rates under 'Performance' in Nagios, can futher provide instant visual indication in Nagios XI of power changes.


### Description
Used for montioring American Power Conversion APC UPS using apcupsd (3.14.12) on RaspberryPi 2B+ for a fun project. I did this because I like Pi, Nagios, flashing lights, servers, and colorful interactive charts :-) 

Power consumption, watts, is calculated because the UPS that I had to develop with didn't report that value but was extracted dividing `load %` and the maximum load `NOMPOWER` value.

### Options

If specifying the -T or -t  for time based alerts you must define them both. When using time based thresholds performance data will be charted in minutes.

~~~
Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit

  Generic options:
    -d, --debug         enable debugging outputs
    -H HOST, --host=HOST
                        host of appcupsd
    -X LINE_LEVEL, --line-level=LINE_LEVEL
                        Volts of power outlet to detect no power if less than
                        the line level

  Monitoring options:
    -P, --enable-perfdata
                        enables performance data (default: no)

  Threshold options:
    -w VOLTS, --battv-warning=VOLTS
                        Defines battery voltage warning threshold (default:
                        24)
    -W VOLTS, --battv-critical=VOLTS
                        Defines battery voltage critical threshold (default:
                        23.3)
    -l PERCENT, --load-warning=PERCENT
                        Defines load warning threshold in percent (default:
                        50%)
    -L PERCENT, --load-critical=PERCENT
                        Defines load critical threshold in percent (default:
                        80%)
    -b PERCENT, --battery-warning=PERCENT
                        Defines battery load warning threshold in percent
                        (default: 30%)
    -B PERCENT, --battery-critical=PERCENT
                        Defines battery load critical threshold in percent
                        (default: 15%)
    -t TIME, --time-warning=TIME
                        Defines battery time left warning threshold in minutes
                        (default: empty). If defined you must also define
                        time-critical
    -T TIME, --time-critical=TIME
                        Defines battery time left critical threshold in
                        minutes (default: empty). If defined you must also
                        define time-warning
    -u WATTS, --consumption-warning=WATTS
                        Defines power consumption warning threshold in watts
                        (default: empty)
    -U WATTS, --consumption-critical=WATTS
                        Defines power consumption critical threshold in watts
                        (default: empty)
~~~

### Credits
* https://github.com/stdevel
