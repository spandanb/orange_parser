#/usr/bin/env bash

####################################################
###             INSTALLATION                     ###
####################################################

#Install Ryu
sudo apt-get update
sudo apt-get -y install git python-pip python-eventlet
sudo pip install oslo.config webob routes
git clone git://github.com/osrg/ryu.git
cd ryu
sudo python setup.py install

#Install cbench
cd ~
git clone https://github.com/mininet/oflops.git
git clone https://github.com/mininet/openflow.git
sudo apt-get install autoconf automake libtool libsnmp-dev libpcap-dev libconfig8-dev -y
cd oflops
sh ./boot.sh
./configure --with-openflow-src-dir=/home/ubuntu/openflow
make

####################################################
###                     RUN                      ###
####################################################

#Run tmux
SESSION=ryu
tmux new-session -d -s $SESSION

tmux rename-window -t $SESSION:0 'ryu'
#run ryu using the simple_switch controller
tmux send-keys "cd ~/ryu && PYTHONPATH=. ./bin/ryu-manager ryu/app/simple_switch.py" C-m

tmux new-window -t $SESSION:1 -n 'cbench'
tmux send-keys "cd ~/oflops/cbench && ./cbench" C-m

