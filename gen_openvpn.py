"""
Reads the config file and generates a host and run file for installing openvpn
on master (server) and clients.
"""
from utils.io_utils import read_yaml
import os

NODESFILE="./nodes.yaml"

def main():
    nodes = read_yaml(NODESFILE)
    
    nodes = (node['ip'] for node in nodes if not node['role'] == 'master')
    #node1 == server, node2 == client1, node3 == client2
    node1, node2, node3 = next(nodes), next(nodes), next(nodes)

    #generate hosts file
    with open('./openvpn/bridge0/hosts', 'w') as fptr:
        fptr.write("[server]\n")
        fptr.write("{} ansible_user=ubuntu\n".format(node1))

        fptr.write("[clients]\n")
        fptr.write("{} ansible_user=ubuntu\n".format(node2))
        fptr.write("{} ansible_user=ubuntu\n".format(node3))

    #generate run file
    with open('./openvpn/bridge0/run.sh', 'w') as fptr:
        fptr.write('#!/bin/bash\n')
        fptr.write('ansible-playbook -i hosts --extra-vars="server_ip={}" openvpn.yaml\n'.format(node1))


if __name__ == "__main__":
    main()
