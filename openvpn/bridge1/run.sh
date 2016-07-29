#!/bin/bash
ansible-playbook -i hosts --extra-vars="server_ip=54.205.138.151" openvpn.yaml
