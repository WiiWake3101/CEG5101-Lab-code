#!/bin/bash
# usage: ./run_client.sh <scenario_name>
cd /home/wiiwake_3101/CEG5101-Lab-code
python3 ts_wrap.py iperf3 -c 10.0.0.6 -p 5201 -u -b 5M -t 90 -i 1 > ${1}_iperf.log
