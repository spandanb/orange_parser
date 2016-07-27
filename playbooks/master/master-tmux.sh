#!/bin/bash

#TMUX Session
SESSION=stack

#Create a new session called $SESSION
tmux new-session -d -s $SESSION >> /home/ubuntu/foo

##create a new window called foo
#tmux new-window -t $SESSION:1 -n 'foo'
##stuff the command 'echo foo' 
#tmux send-keys "echo foo" C-m

sleep 5

tmux new-window -t $SESSION:1 -n 'w-sync'
tmux send-keys "cd /opt/stack/whale && /opt/stack/whale/bin/whale-init --config-file /etc/whale/whale.conf" C-m

sleep 2

tmux new-window -t $SESSION:2 -n 'w-api'
tmux send-keys "cd /opt/stack/whale && /opt/stack/whale/bin/whale-server --config-file /etc/whale/whale.conf" C-m

sleep 2

tmux new-window -t $SESSION:3 -n 'ryu'
tmux send-keys "cd /opt/stack/ryu && /opt/stack/ryu/bin/ryu-manager --flagfile /etc/ryu/ryu.conf" C-m

sleep 2 

tmux new-window -t $SESSION:4 -n 'janus'
tmux send-keys "sleep 10;cd /opt/stack/janus && /opt/stack/janus/bin/janus-init --config-file /etc/janus/janus.conf" C-m

sleep 2

tmux new-window -t $SESSION:5 -n 'vino'
tmux send-keys "cd /home/ubuntu/vino_orc; git fetch; git checkout no_password; sleep 60;python ./master.py -i `cat ext_ip` -n nodes.yaml -e edges.yaml" C-m

sleep 2
tmux new-window -t $SESSION:6 -n 'portal'
tmux send-keys "cd /home/ubuntu/blade; sleep 30; python ./manage.py migrate; sudo python manage.py runserver 0.0.0.0:80" C-m

touch fooooooo
