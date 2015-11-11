#!/usr/bin/python

__author__ = 'lsteng'


"""
This module implements the client software running on a KVM guest.  
A KVM guest can issue performance monitoring request to host machine via this client by using command line. For detailed usage,
run
    ./guest_client -h 
in a command line window.    

The client starts a program on the guest KVM while configuring the performance monitor on the host machine to monitor 
the guest when running the program. There is no limitation on the kind of the program. User can run 

    ./guest_client -p "sleep 10" 

to do nothing but monitor the guest for 10 seconds.


Users may need set the host's IP address and the port number, if they are different than the defaults. For setting  IP
address and port number, add --host [newIP] --port [portID] to the command line. For example:

    ./guest_client -p "sleep 10" --host 192.168.122.2 --port 9998


"""


import socket
import sys
import os
import argparse
import command_parse as cp
import json
from time import sleep
from uuid import getnode as get_mac

import multiprocessing
import datetime

#parse the MAC of the guest
#mac = open('/sys/class/net/eth0/address').read()

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



# this function receives the performance monitoring data from the host server, and display it on the guest.
def receive (sock):
    for line in sock.makefile('r'):
        print line
    tm=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')    
    print tm+"\tfinished"



try:
    # parse the command line request
    msg=cp.perf_parse()


    # get the IP address and port number of the server running on the host. By default, the IP address is 
    # 192.168.122.1. If user want to change this address, add --host [newIP] to the command line when starting 
    # the client.

    # User may also change the port number if the server's port number is different to 9995. Just modify here

    HOST, PORT = [msg['ip'], msg['port']]


    # Connect to the server 
    sock.connect((HOST, PORT))
   
    # convert the command line request to Json format
    jmsg = json.dumps(msg)

    #print jmsg

    # send the command line request to the server 
    sock.sendall(str(jmsg)+"\n")

    sleep(0.1)
    # start the receiver thread
    prec= multiprocessing.Process(target = receive, args=(sock,) )
    
        
    prec.start()

    
    tm=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    print tm+"\tbegin execute "+msg['program']

    # start to running a program on the guest
    os.system(msg['program'])
    command = "end"

    # once the program finishes, stop the monitor on the server
    sock.sendall(command+"\n")

except socket.error as (errno, string):
        print("Error " + repr(errno) + ": " + string)
        exit(0)
  

except KeyboardInterrupt:
    prec.terminate()
    sock.close()
    print "finished"
    exit(0)
except Exception as e:
        print(e)     
finally:
    
    sock.close()
   