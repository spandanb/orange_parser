

"""
Vino templates describe the topology to be deployed and configured.  In some
cases, you want acccess to entities that exist outside the topology.  This is
where (special) forms come in.  Forms are functions that can contain arbitrary
logic. These forms get invoked at either deploy or config.
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

def resolve_parse(form, params):
    """
    There are some special functions that can 
    be used in template files. An example is
    "aws::get_image_id(`image_name`)".

    These need to be identified and resolved.
    These refer to special functions accessible at parse time.
    These forms can't be nested. 
    """
    #Check if indeed this object needs to be resolved
    if not needs_resolve(form): return form
    namespace, method, args = get_components(form)

    #Namespaces have a 1-1 mapping to modules
    #import importlib
    #module = importlib.import_module(namespace)

    if namespace == "aws":
        if method == "get_image_id":
            ubuntu_amis = {
                'us-east-1':'ami-fce3c696', #N. Virginia
                'us-west-1':'ami-06116566', #N. California
                'us-west-2':'ami-9abea4fb', #Oregon
            }
            return ubuntu_amis[os.environ["AWS_DEFAULT_REGION"]]
        else:
            print "Method {} not found".format(method)
    elif namespace == "utils":
        if method == "get_param":
            return params[args[0]]
        else:
            print "Method {} not found".format(method)

    else:
        print "Namespace {} not found".format(namespace)
   

def resolve_config(form, ip=''):
    """
    These are the analogue special functions
    that can be invoked during instantiation
    e.g. install ovs.

    """
    if not needs_resolve(form): return form
    namespace, method, args = get_components(form)

    if namespace == "utils":
        if method == "install_openvswitch_2_3_3":
            print "In install_openvswitch_2_3_3 ..."
            #NOTE: See if there is better way
            os.system('scp install_ovs.sh ubuntu@{}:/home/ubuntu'.format(ip) )
            os.system("ssh ubuntu@{} '/home/ubuntu/install_ovs.sh'".format(ip) )

        else:
            print "Method {} not found".format(method)
    else:
        print "Namespace {} not found".format(namespace)
