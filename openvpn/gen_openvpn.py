"""
Reads the config file and generates a host and run file for installing openvpn
on master (server) and clients.
"""
import os, pdb, yaml

def read_yaml(filepath):
    with open(filepath, 'r') as stream:
        return yaml.load(stream)

def run_file(filepath, server, master):
    "Creates the run.sh file"
    with open(filepath, "w") as fptr:
        fptr.write('#!/bin/bash\n')
        fptr.write('ansible-playbook -i hosts --extra-vars="server_ip={} master_ip={}" openvpn.yaml\n'.format(server, master))

def hosts_file(filepath, nodes, server):
    "Creates the inventory file"
    with open(filepath, "w") as fptr:
        fptr.write("[univ]\n")
        for node in nodes:
            fptr.write("{} ansible_user=ubuntu\n".format(node))

        fptr.write("[server]\n")
        fptr.write("{} ansible_user=ubuntu\n".format(server))

        fptr.write("[clients]\n")
        for node in nodes:
            fptr.write("{} ansible_user=ubuntu\n".format(node))

def main_local():
    "This is the case where there is no SDI master node"
    NODESFILE = "../nodes.yaml"
    nodes = read_yaml(NODESFILE)
    nodes = [node['ip'] for node in nodes if not node['role'] == 'master']
    
    master = server = nodes[0]
    
    #generate hosts file
    hosts_file('./bridge0/hosts', nodes, server)

    #generate run file
    run_file('./bridge0/run.sh', server, master)

def main_master():
    """
    Same as master, except meant to be run on the master node
    """
    NODESFILE = "/home/ubuntu/vino_orc/nodes.yaml"
    nodes = read_yaml(NODESFILE)
    nodes = [node['ip'] for node in nodes if not node['role'] == 'master']
    
    server = nodes[0]
    with open("/home/ubuntu/vino_orc/ext_ip") as fptr:
        master = fptr.read().strip()

    #generate hosts file
    hosts_file('/home/ubuntu/openvpn/bridge0/hosts', nodes, server)

    #generate run file
    run_file('/home/ubuntu/openvpn/bridge0/run.sh', server, master)


if __name__ == "__main__":
    main_local()
