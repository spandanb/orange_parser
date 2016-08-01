#!/bin/bash

####################################
# Tear Down Ethernet bridge on Linux
####################################

# Define Bridge Interface
br="br-int"

eth="q1"

# Define list of TAP interfaces to be bridged together
tap="tap0"

sudo ifconfig $eth down
sudo ovs-vsctl del-br $br

for t in $tap; do
    sudo openvpn --rmtun --dev $t
done
