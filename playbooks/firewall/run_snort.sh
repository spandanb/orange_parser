#!/bin/bash
sudo killall snort
cd /home/ubuntu
ping `cat gateway_ip` &
ping `cat webserver_ip` &

mkdir -p /home/ubuntu/log
until sudo snort -D -Q --daq afpacket -i p2:p3 -c /home/ubuntu/snort.conf -l /home/ubuntu/log
do
echo "Re-Try in 5 seconds"
sleep 5
done
