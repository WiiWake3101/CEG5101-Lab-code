#!/bin/bash
# usage: ./monitor.sh <scenario_name> <target_ip>
timeout 70 ping -D -i 0.2 "$2" > "${1}_ping.log"
echo "DONE: saved to ${1}_ping.log"
