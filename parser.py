#!/usr/bin/python2.7
"""
Parses topology and instantiates nodes.
"""

from multi.aws import get_aws_client, ubuntu
from vino.servers import get_savi_client
import sys, os, pdb, argparse
import base64, time
from utils.io_utils import read_yaml, write_yaml, log, yaml_to_envvars
from utils.utils import create_and_raise
from ansible_wrapper import ansible_wrapper
from form_resolver import resolve_form
from itertools import combinations
import time

##############################################
################     TODO     ################
##############################################
"""
1) user_data for SAVI nodes
"""

##############################################
################    CONSTS    ################
##############################################
NODESFILE="./nodes.yaml"
EDGESFILE="./edges.yaml"
NODES_ABBR_FILE="./nodes.txt"
CONFIG_FILE="config.yaml"


def parse_declaration(declaration):
    """
    Parse declarations 
    This includes security group.

    TODO: add support for keyname
    """
    decl = {'type': declaration["type"]}
    if decl["type"] == "security-group":
        decl["name"] = declaration["name"]
        decl["description"] = declaration["description"]
        decl["ingress"] = declaration.get("ingress") or []
        decl["egress"] = declaration.get("egress") or []
    
    return decl

def parse_node(resc, params):
    """
    Parse a node object.
    There are a few special cases to handle
    If optional fields are not specified, then behaviod is undef

    Currently only handles virtual-machines
    """
    #TODO: Error checking; 

    node = {}
    #required fields
    node["image"]  = resolve_form(resc["image"], params=params)
    node["flavor"] = resc["flavor"]
    node["name"]   = resc["name"]
    node["type"]   = resc["type"]

    #Optional Fields
    node["secgroups"] = resc.get("security-groups", [])
    node["key_name"]  = resolve_form(resc.get("key-name"), params=params)
    node["region"]    = resc.get("region", "CORE")
    node["role"]      = resc.get("role") #TODO: should be a list
    
    if resc.get("provider", "savi") == "savi":
        node["provider"]  = "savi" 
        node["tenant"]    = resc["tenant"]
        node["floating_ip"] = resc.get("assign-floating-ip", False)
    else:
        node["provider"] = resc.get("provider")
        if node["provider"] != "aws":
            create_and_raise("InvalidProviderException", "Provider must be 'savi' or 'aws'") 

    #TODO: check whether need to base64 encode, AWS docs say so, but works w/o anyways
    node["user_data"] = resc.get("user-data", '')
   
    node["config"] = resc.get("config", []) 
    
    return node

def parse_edge(edge):
    """
    parse an edge object.
    """
    return edge

def mesh_network(nodes):
    """
    Returns the mesh representation of the list of nodes
    """
    return list(combinations(map(lambda node: node["name"], nodes), 2))

def parse_template(template, user_params):
    """
    Reads topology file and creates required topology
    """
    topology = read_yaml(filepath=template)
    
    #Parse the parameters from the topology file
    if "parameters" in topology:
        topo_params = topology["parameters"].keys()
        params = resolve_params(topo_params, user_params)
    else:
        params = {}

    #Parse the declarations 
    if "declarations" in topology:
        others =[parse_declaration(dec) for dec in topology["declarations"]]
    else:
        others = []

    #Parse the nodes
    if "nodes" in topology:
        nodes = [parse_node(resc, params) for resc in topology["nodes"]]
    else:
        nodes = []

    #Parse the edges
    if "edges" in topology and topology["edges"]:
        edges = [parse_edge(resc) for resc in topology["edges"]]
    else:
        edges = mesh_network(nodes)



    return others, nodes, edges

def resolve_params(topo_params, user_params):
    """
    Parameters must be passed in the command line
    or be set as environment variables.
    """
    resolved = {}
    #Resolve based on user specified parameters
    if user_params: 
        for pair in user_params.split(" "):
            pname, pvalue = pair.split("=")
            if pname in topo_params:
                resolved[pname] = pvalue
                topo_params.remove(pname)
            else:
                create_and_raise("InvalidParamException", 
                                 "Unknown parameter: '{}' specified.".format(pname))

    #Resolve based on env vars
    for param in topo_params:
        value = os.environ.get(param)
        if not value: 
            create_and_raise("UnspecifiedParameterException",
                             "The parameter {} is undefined".format(param))
        else:
            resolved[param] = value

    return resolved

def instantiate_others(others):
    """
    Instantiate the other resources 
    """
    aws =  get_aws_client()
    savi = get_savi_client()  

    for other in others:
        if other["type"] == "security-group":
            log("Creating secgroup {}".format(other["name"]))
            rules = {"ingress": other.get("ingress", []), "egress": other.get("egress", [])}
            
            #Creates rules on both AWS and SAVI for current specified region, tenant    
            aws_id = aws.create_secgroup(other["name"], rules, description=other.get("description"))
            savi_id = savi.create_secgroup(other["name"], rules, description=other.get("description"))

            other["aws-id"] = aws_id
            other["savi-id"] = savi_id


def instantiate_nodes(nodes):
    """
    Instantiate the nodes
    """
    aws =  get_aws_client()
    savi = get_savi_client()  
    
    #Only need to sync the key's once
    savi_key_synced = False
    aws_key_synced = False

    #Instantiation Loop
    for node in nodes:
        if node["provider"] == "savi":
            if not savi_key_synced:
                savi.sync_savi_key(node["key_name"])
                savi_key_synced = True
            
            log("Booting {} in SAVI".format(node["name"]))
            #node["id"] = savi.create_server(node['name'], node['image'], node['flavor'], secgroups=node["secgroups"], key_name=node["key_name"])

        else: #aws
            if not aws_key_synced:
                aws.sync_aws_key(node["key_name"])
                aws_key_synced = True

            log("Booting {} in AWS".format(node["name"]))
            #node["id"] = aws.create_server(node["image"], node["flavor"], keyname=node["key_name"], user_data=node["user_data"], secgroups=node["secgroups"])[0]
    return

    #Waiting-until-built loop
    for node in nodes:
        if node["provider"] == "savi":
            node_ip = savi.wait_until_sshable(node["id"])
            #The property 'ip' has value of floating-ip if defined, else ip
            if node["floating_ip"]:
                log("Requesting floating IP for {}".format(node["id"]))
                node["ip"] = savi.assign_floating_ip(node["id"])
                node["int_ip"] = node_ip
            else:
                node["ip"] = node_ip
        else: #aws
            node["ip"] = aws.get_server_ips([node["id"]])[0]
    
    #Print some info 
    for node in nodes:
        log("{}({}) is available at {}".format(node["name"], node["id"], node["ip"]))

    return nodes

def configure_nodes(nodes, config):
    """
    Configure each of the nodes
    """
    for node in nodes:
        #a node has a list of configurations
        for conf in node["config"]:
            #resolve extra vars if needed
            if "extra-vars" in conf:
                extra_vars = {name: resolve_form(val, nodes=nodes)
                             for name, val in conf["extra-vars"].items()}
            else:
                extra_vars = {}

            log("Running {} on {}".format(conf["playbook"], node["name"]))
            log("extra_vars is {}".format(extra_vars))
            ansible_wrapper.playbook(playbook=conf["playbook"],
                                     hosts={conf["host"]: node["ip"]}, 
                                     extra_vars=extra_vars)
        

def write_results(nodes, edges):
    """
    Writes the results to file
    """
    write_yaml(nodes, filepath=NODESFILE) 
    with open(NODES_ABBR_FILE, 'w') as fileptr:
        for node in nodes: 
            fileptr.write("{}: {}\n".format(node["name"], node["ip"]))

    write_yaml(edges, filepath=EDGESFILE)    

def read_nodes_edges():
    """
    Read the nodes and edges file and returns the object.
    For debugging / plug and play purposes, i.e. nodes are provisioned
    but need to be configured.
    """
    nodes = read_yaml(filepath=NODESFILE)
    edges = read_yaml(filepath=EDGESFILE)
    return nodes, edges
            
def cleanup():
    """
    Reads last created topology and deletes it
    """
    try:
        nodes = read_yaml(filepath=NODESFILE)
    except IOError:
        log("Nothing to delete....")
        return 

    if not nodes:
        log("Nothing to delete....")
        return 

    is_savi = lambda node: "provider" not in node or node["provider"] == "savi"
    is_aws = lambda node: "provider" in node and node["provider"] == "aws"
    savi_nodes = [node for node in nodes if is_savi(node)]
    aws_nodes = [node['id'] for node in nodes if is_aws(node)]
  
    #Lazy load the clients
    if savi_nodes: savi = get_savi_client()  
    if aws_nodes: aws = get_aws_client()

    log("Deleting on SAVI nodes...")
    for node in savi_nodes:
        log("Deleting {} ({})".format(node["name"], node["id"]))
        try:
            savi.delete_servers(server_id=node["id"])
        except ValueError as err:
            log("Warning: nodes file ({}) may be out of sync".format(NODESFILE))
    
    log("Deleting AWS nodes...")
    for node in aws_nodes: 
        log("deleting {}".format(node))
    try:
        aws.delete_servers(aws_nodes)
    except: 
        log("Warning: nodes file ({}) may be out of sync".format(NODESFILE))

    #Nuke the files
    with open(NODESFILE, 'w') as fileptr:
        fileptr.write('')
    with open(NODES_ABBR_FILE, 'w') as fileptr:
        fileptr.write('')

def nuke_aws():
    """
    Deletes all AWS nodes
    """
    log("Deleting ALL AWS nodes...")
    aws = get_aws_client()
    aws.delete_all()

def nuke_savi(prefix):
    """
    Deletes all SAVI nodes
    """
    log("Deleting ALL SAVI nodes with prefix {}...".format(prefix))
    savi = get_savi_client()
    savi.delete_servers(name_prefix=True, name=prefix)

def create_master(config):
    """
    Provisions the master node. 
    Returns the node object of the master including the configs.
    """
    savi = get_savi_client()  
    secgroup = "vino-master"
    node = {"name"     : "vino-master",
            "image"    : "master-sdi.0.7",
            "flavor"   : "m1.medium",
            "role"     : "master", 
            "secgroups": [secgroup]}

    #First create a secgroup for master node 
    rules = {"ingress": [{'to':22,'from':22, 'protocol':'tcp', 'allowed':['0.0.0.0/0'] },
                         {'to':80,'from':80, 'protocol':'tcp', 'allowed':['0.0.0.0/0'] },
                         {'to':6633,'from':6633, 'protocol':'tcp', 'allowed':['0.0.0.0/0'] },
                         {'to':-1,'from':-1, 'protocol':'icmp', 'allowed':['0.0.0.0/0'] }],
             "egress": []
            }
    log("creating secgroup: {}".format(secgroup))
    savi.create_secgroup(node["secgroups"][0], rules, "Security rules for the vino master node" )
    
    node["id"] = savi.create_server("vino-master", "vino_master_v1", "m1.medium", 
                                   secgroups=[secgroup], key_name=config["savi_key_name"])
    log("waiting for master to be SSHable")
    if config["assign_master_fip"]:
        node["int_ip"] = savi.wait_until_sshable(node["id"])
        node["ip"] = savi.assign_floating_ip(node["id"])
    else:
        node["ip"] = savi.wait_until_sshable(node["id"])
    time.sleep(5) #weird that this is needed

    conf = {
        "playbook"  : './playbooks/master/master.yaml',
        "extra-vars": {"master_ip": node["ip"]},
        "host"     : "master"
    } 
    #This is the format that the configure_nodes expects
    node["config"] = [conf]

    return node


def parse_args():
    """
    Parse arguments and call yaml parser
    """
    #If parser gets too complex, consider: http://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
    parser = argparse.ArgumentParser(description='Vino command line interface')
    
    parser.add_argument('-f', '--template-file', nargs=1, help="specify the template to use")
    parser.add_argument('-p', '--parameters', nargs=1, help="parameters to the template")
    parser.add_argument('-c', '--clean-up', action="store_true", help="Deletes any provisioned topologies")
    parser.add_argument('-n', '--nuke-aws', action="store_true", help="Deletes all aws instances")
    parser.add_argument('--nuke-savi', nargs=1, help="Deletes all savi instances matching with the specified prefix")
    parser.add_argument('-d', '--debug', action="store_true", help="Only performs config; requires nodes and edges files to be populated")

    args = parser.parse_args()

    #Do this since the envvars are required by multiple sub commands.
    #sets the key-value pairs in CONFIG_FILE as envvars
    yaml_to_envvars(CONFIG_FILE)
    config = read_yaml(CONFIG_FILE)

    if args.clean_up:  
        cleanup()

    elif args.nuke_aws:
        nuke_aws()

    elif args.nuke_savi:
        prefix = args.nuke_savi[0]
        nuke_savi(prefix)
        return 

    elif args.template_file:
        #get value of arguments 
        template = args.template_file[0]
        parameters = args.parameters[0] if args.parameters else None
        
        #resolve 
        others, nodes, edges = parse_template(template, parameters)
        #instantiate other declarations
        #others = instantiate_others(others)

        #instantiate nodes 
        nodes = instantiate_nodes(nodes)
        return  
        #create master
        if config["create_master"]:
            #don't modify original nodes array; don't want to call configure_nodes on master node
            mnode = create_master(config)
            nodes.append(mnode)
            write_results(nodes, edges)
        else:
            write_results(nodes, edges)
        
        #Configure the nodes
        configure_nodes(nodes, config)

    elif args.debug:
        #Only runs the configuration scripts
        nodes, edges = read_nodes_edges()
        #Configure the nodes
        configure_nodes(nodes, config)

    else:
        parser.print_help()
        create_and_raise("TemplateNotSpecifiedException", "Please specify a template file")
        
if __name__ == "__main__":
    start_time = time.time()
    parse_args()
    print(time.time() - start_time)

