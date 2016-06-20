import os, sys, time, pdb
import daemon
import psutil
import imp
import requests

#See: https://www.python.org/dev/peps/pep-3143/#slack-daemon
#for using daemon

def simple_example():
    "Simple example of how the daemon works"
    with daemon.DaemonContext():
        #The following can be wrapped in a function
        while True:
            with open("/home/ubuntu/current_time.txt", "a") as f:
                f.write("The time is now " + time.ctime())
                time.sleep(5)


def start_daemon(eventfunc, master_endpoint=''):
    """
    Start daemon that runs eventfunc  
    Arguments:- 
        eventfunc: function that returns True when user event happened
        master_endpoint: the endpoint to notify when an event occurs
    """
    with daemon.daemoncontext():
        while True:
            #eventfunc() returns True if event happened
            resp = eventfunc()
            if resp: 
                request.get(master_endpoint)
                #Terminate?


def main(eventfile):
    #Load user module
    usrmodule = imp.load_source('event', eventfile)
    #get all the events specified by the user
    #NB: event classes must have 'Event' in name
    events = [ getattr(usrmodule, mem) for mem in dir(usrmodule) if "Event" in mem]
        
    for event in events:
        #this is the node where we want to detect the event
        print event.node_name
        #this is the event itself; wrap this in `start_daemon` func and run on node
        #ideally the event should be a stateless boolean function that can be run periodically
        #to detect an event; although more complicated events may be possible
        print event.event 
        #this should be the response to the event happening; run on master/controller node
        print event.response

if __name__ == "__main__":
    #this should be a path to the event file
    if len(sys.argv) == 2 or not os.path.isfile(sys.argv[1])
        print "Usage: eventlib.py <eventfile>"
        sys.exit(1)
    else:
        main(sys.argv[1])
