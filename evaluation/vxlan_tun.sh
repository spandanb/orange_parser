#!/bin/sh

#Creates a decentralized bridge and sets up VXLAN tunnel

if [ -z "$1" ]; then
    echo "Usage: vxlan_tun.sh <<remote IP>>"
    exit 0
fi

remote_ip=$1
#Name of bridge
bridge=br-int
port_name=vx1

local_ip=`ifconfig eth0 | grep 'inet addr:'| cut -d: -f2 | awk '{ print $1}'`
overlay_ip=`echo $local_ip | awk '{split($0, a,"."); print "192.168."a[3]"."a[4]}'`

#Remove bridge
sudo ovs-vsctl -- --if-exists del-br $bridge
#Remove p1 interface
sudo ifconfig p1 down

sudo ovs-vsctl add-br $bridge
sudo ovs-vsctl add-port $bridge $port_name -- set interface $port_name type=vxlan options:remote_ip=$remote_ip options:key=1

sudo ovs-vsctl -- --may-exist add-port $bridge p1 -- set interface p1 type=internal
sudo ifconfig p1 $overlay_ip/16 up
sudo ifconfig p1 mtu 1400 up
