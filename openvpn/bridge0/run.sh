#!/bin/bash
ansible-playbook -i hosts --extra-vars="server_ip=52.87.215.2" openvpn.yaml
