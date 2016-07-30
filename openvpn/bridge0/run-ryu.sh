#/usr/bin/env bash

sudo apt-get -y install git python-pip python-eventlet
sudo pip install oslo.config webob routes

#from source
git clone git://github.com/osrg/ryu.git
cd ryu
sudo python setup.py install

#Run in tmux
SESSION=ryu
tmux new-session -d -s $SESSION

#tmux new-window -t $SESSION:1 -n 'ryu'
tmux rename-window -t $SESSION:0 'ryu'
#to run ryu using the simple_switch controller
tmux send-keys "cd ~/ryu && PYTHONPATH=. ./bin/ryu-manager ryu/app/simple_switch.py" C-m

