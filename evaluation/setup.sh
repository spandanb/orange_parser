#!/bin/bash

#Run this script to run cbench test with Ryu on new node

if [ -z $1 ]; then
    echo "Usage: ./setup.sh <machine IP>"
    exit 1
fi

#The machine running the test
nodeip=$1
node=ubuntu@$nodeip
scppath=$node:~

ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R $nodeip

ssh $node wget https://raw.githubusercontent.com/spandanb/utils/master/.tmux.conf

scp run_ryu_test.sh $scppath

ssh $node ./run_ryu_test.sh
