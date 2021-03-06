#!/bin/bash

#################################
# Set up Ethernet bridge on Linux
# Requires: bridge-utils
#################################

controller=tcp:$1:6633

# Define Bridge Interface
br="br-int"

# Define list of TAP interfaces to be bridged,
# for example tap="tap0 tap1 tap2".
tap="tap0"

#eth0 IP Addr
myip=`ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'`
#Overlay IP Addr
lip=`echo $myip | awk '{split($0, a, "."); print "172.16." a[3] "." a[4]}'`
echo My IP addr is $myip
echo Overlay IP addr is $lip

# Define physical ethernet interface to be bridged
# with TAP interface(s) above.
eth="q1" #This is the 'port' in ovs
eth_ip=$lip

for t in $tap; do
    sudo openvpn --mktun --dev $t
done
 
#brctl addbr $br #ADD BRIDGE
sudo ovs-vsctl add-br $br
sudo ovs-vsctl set-controller $br $controller
sudo ovs-vsctl set br $br protocols=OpenFlow10
sudo ovs-vsctl set-fail-mode $br secure
sudo ovs-vsctl set controller $br connection-mode="out-of-band"

#brctl addif $br $eth #ADD INTERFACE/PORT
sudo ovs-vsctl add-port $br $eth  -- set interface $eth type=internal

for t in $tap; do
    #brctl addif $br $t
    sudo ovs-vsctl add-port $br $t
done

for t in $tap; do
    sudo ifconfig $t 0.0.0.0 promisc up
done

#sudo ifconfig $eth 0.0.0.0 promisc up

#sudo ifconfig $br $eth_ip netmask $eth_netmask broadcast $eth_broadcast
sudo ifconfig $eth $eth_ip/16 up

