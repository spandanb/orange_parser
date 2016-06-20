import pdb
import psutil
import requests
import ast

#psutils must exist on the host machine
#example events
def to_human(num, suffix='B'):
    """
    Returns human readable repr of num
    src: http://stackoverflow.com/questions/1094841
    """
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "{:.1f}{}{}".format(num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def percent_free_memory(percent):
    "returns True if free memory is less than `percent`"
    vmem = psutil.virtual_memory()
    return vmem.free / float(vmem.total) < percent
    
def free_memory(amount):
    "returns True if free memory is less than `amount`"
    vmem = psutil.virtual_memory()
    return vmem.free < amount


class Event1(object):
    
    node_name = "vino-firewall"
    
    @staticmethod
    def event():
        "returns True if free memory is less than `amount`"
        amount = 1000000000 #~1GB
        vmem = psutil.virtual_memory()
        return vmem.free < amount
        
    @staticmethod
    def response():
        clone("vino-firewall")


