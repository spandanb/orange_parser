#!/bin/bash
ansible-playbook -i hosts --extra-vars "webserver_ip=192.168.205.185 gateway_ip=192.168.194.82" wordpress.yaml
