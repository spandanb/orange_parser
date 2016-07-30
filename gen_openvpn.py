"""
Reads the config file and generates a host and run file for installing openvpn
on master (server) and clients.
"""
from utils.io_utils import read_yaml
import os, pdb

NODESFILE="./nodes.yaml"

def main():
    nodes = read_yaml(NODESFILE)
    
    nodes = [node['ip'] for node in nodes if not node['role'] == 'master']
    server = nodes[0]

    #generate hosts file
    with open('./openvpn/bridge0/hosts', 'w') as fptr:
        fptr.write("[server]\n")
        fptr.write("{} ansible_user=ubuntu\n".format(server))

        fptr.write("[clients]\n")
        for node in nodes:
            fptr.write("{} ansible_user=ubuntu\n".format(node))

    #generate run file
    with open('./openvpn/bridge0/run.sh', 'w') as fptr:
        fptr.write('#!/bin/bash\n')
        fptr.write('ansible-playbook -i hosts --extra-vars="server_ip={}" openvpn.yaml\n'.format(server))


if __name__ == "__main__":
    main()
