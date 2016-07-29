#!/bin/bash
ansible-playbook -i hosts --extra-vars "master_ip=142.150.208.221" master.yaml -vv
