"""
Temporary module since actual ansible_wrapper is buggy
"""
from tempfile import NamedTemporaryFile 
import os

#The following are transformation functions; transforms input to required form for ansible_playbook
def _hosts(hosts):
    """
    Takes the host object and makes a tmp file with it
    """
    #Transform hosts object to string
    if type(hosts) is str:
        inv = "[run_hosts]\n{}".format(hosts)

    elif type(hosts) is list:
        inv = "[run_hosts]\n"
        inv += "\n".join(["{}".format(h) for h in hosts])

    elif type(hosts) is dict:
        inv = ""
        for group, nodes in hosts.items():
            inv += "[{}]\n".format(group)
            if type(nodes) is list:
                inv += "\n".join(["{} ansible_user=ubuntu".format(n) for n in nodes])
            else: #str
                inv += nodes 
            inv += "\n"

    #Write `inv`entory to a tmpfile
    invfile = NamedTemporaryFile(dir=os.getcwd())
    invfile.write(inv)
    invfile.flush()
    return invfile

def _extra_vars(extra_vars):
    """
    equals encode extra_vars dict
    e.g. 
    {'a':1, 'b':2} -> "a=1 b=2"
    """
    if not extra_vars:
        return None

    encoded = '"'
    for var, val in extra_vars.items():
        encoded += "{}={} ".format(var, val)    
    return encoded + '"'

class ansible_wrapper(object):
    @staticmethod
    def playbook(playbook=None, hosts=None, 
                 private_key_file='~/.ssh/id_rsa', 
                 verbosity=1,
                 remote_user='ubuntu', 
                 extra_vars={}):
        """
        Calls a playbook specified by the user.
        Utility function that mimics call to ansible_wrapper 
    
        Arguments:-
            playbook:- path to playbook
            host:- string representing host
            remote_user:- the remote user
            extra_vars: a dict of extra vars
        """
        cmd = ["ansible-playbook"]

        hosts = _hosts(hosts)
        cmd.append( "-i")
        cmd.append(hosts.name)

        extra_vars = _extra_vars(extra_vars)
        if extra_vars:
            cmd.append("--extra-vars")
            cmd.append(extra_vars)
            
        cmd.append(playbook)

        if verbosity > 0:
            cmd.append("-" + "v"*verbosity)

        #print "Running command {}".format(" ".join(cmd))

        os.system(" ".join(cmd))

        #deletes hosts file
        hosts.close()
