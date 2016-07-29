#!/bin/bash

sudo iptables -A INPUT -i tap0 -j ACCEPT
sudo iptables -A INPUT -i br0 -j ACCEPT
sudo iptables -A FORWARD -i br0 -j ACCEPT
