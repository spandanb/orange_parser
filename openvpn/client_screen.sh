#!/bin/bash

source screen_handler.sh

#Parameter
SESSION=openvpn-client

#create session
create_session $SESSION

sleep 5

#start openvpn client 
screen_it $SESSION openvpn "sudo openvpn client.conf"
