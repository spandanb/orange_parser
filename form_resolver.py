from utils.utils import create_and_raise
import os

"""
Vino templates describe the topology to be deployed and configured.  In some
cases, you want acccess to entities that exist outside the topology.  This is
where (special) forms come in.  Forms are functions that can contain arbitrary
logic. These forms get invoked at either deploy or config.
NB: Currently, forms can't be nested.
"""

def needs_resolve(form):
    """
    Returns True if the form needs to be
    resolved. Checks whether form string contains '::'
    """
    return '::' in form

def get_components(form):
    """
    Returns the components of the special `form`.
    Forms are special functions that can be used in
    vino templates. These include lookup functions.
    The components are the name of the form, its namespace,
    and its arguments.
    """
    namespace, tail = form.split('::')
    tail = tail.replace(')', '') #remove right paren
    method, args = tail.split("(") #split on left-paren
    args = args.split(",")

    return namespace, method, args

def resolve_form(form, params=None, nodes=None, *varargs, **kwargs):
    """
    Resolves deploy-time and parse time forms. This requires
    form names to be unique. 

    Arguments:-
        form: the form to resolve, (string)
        params: the params to the template
        nodes: list of nodes
        args: dict of any unspecified args,
            caller needs to make sure that the method uses the
            appropriate name
    """

    #Check if indeed this object needs to be resolved
    if not needs_resolve(form): return form
    namespace, method, args = get_components(form)

    if namespace == "aws":
        if method == "get_ubuntu_image_id":
            ubuntu_amis = {
                'us-east-1':'ami-fce3c696', #N. Virginia
                'us-west-1':'ami-06116566', #N. California
                'us-west-2':'ami-9abea4fb', #Oregon
            }
            return ubuntu_amis[os.environ["AWS_DEFAULT_REGION"]]
    
    elif namespace == "utils":
        #Lookup a param
        #TODO: To generalize this, need a way of converting user specified params to python datastructs
        if method == "get_param":
            return params[args[0]]

        elif method == "get_ip":
            return next(node["ip"] for node in nodes if node['name'] == args[0])
        
        elif method == "get_overlay_ip":
            return next("192.168.{}.{}".format( *node["ip"].split(".")[2:])
                            for node in nodes if node['name'] == args[0])

        #install OVS
        elif method == "install_openvswitch_2_3_3":
            print "In install_openvswitch_2_3_3 ..."
            #NOTE: See if there is a better way
            os.system('scp install_ovs.sh ubuntu@{}:/home/ubuntu'.format(node["ip"]) )
            os.system("ssh ubuntu@{} '/home/ubuntu/install_ovs.sh'".format(node["ip"]) )

    create_and_raise("ResolveException", 
        "Unable to find either namespace '{}' or method '{}'".format(namespace, method))

if __name__ == "__main__":
    print resolve_form("utils::get_overlay_ip(abcd)", nodes=[{"name":"abcd", "ip":"10.12.1.2"}])

