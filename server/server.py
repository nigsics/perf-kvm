#!/usr/bin/python

# Copyright 2015 SICS Swedish ICT AB
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
This module provides the general functions of a server.
We can start a server by running sudo ./server.py

This server receives and serves requests from guest_clients.
By default, the server's address is set to "192.168.122.1",
port number is "9999".  Users can modify this setting according to their platform.

Functions:

sender(intQueue, request):  the function sends the performance monitoring information back to  a client

MyTCPHandler(SocketServer.StreamRequestHandler):  receiving and handling guest requests from TCP connections


"""





# import subprocess
# import sys
from time import sleep
# #import psutil
import os
# from StringIO import StringIO  # Python2
import sub
import perf_dict
import json
import socket


import SocketServer
import multiprocessing
import Queue
import argparse
from version import __version__

parser = argparse.ArgumentParser(description="Monitor Configuration")
parser.add_argument("--host", help='IP of the computer running the server; default 127.0.0.1', nargs='?', default="192.168.122.1")
parser.add_argument("--port", help='Port of the computer running the server; default 9999', nargs='?', default="9999", type=int)
parser.add_argument('-v',"--version", help='Show version and exit',action='store_true')
args = parser.parse_args()

if args.version is True:
    print(__version__)
    exit(0)


HOST, PORT = args.host, args.port
#mac = open('/sys/class/net/eth0/address').read()

"""
Build a dictionary for every KVM running on the host machine

"""

kvmInfo = perf_dict.perfDict()




"""
send the performance data back to the requesting guest-client

"""

def sender(intQueue, request):
    try:
        while(1):
            data = intQueue.get(True)
            print "sender: "+data

            request.sendall(data)

    except Queue.Empty:
        pass


"""
Handler for the guest-client request
"""


class MyTCPHandler(SocketServer.StreamRequestHandler):


    def handle(self):

        try:

            jmsg = self.rfile.readline().strip()

            #print jmsg

            # guest request is formatted to json.
            # Parse the json message and get the guest mac address and the request details.

            msg = json.loads(jmsg)


            kvmID = msg['mac']

            # print "{} wrote:".format(self.client_address[0])
            # print kvmID


            global kvmInfo
            pid = kvmInfo[kvmID]['pid'][msg['cpu']]
            occupy = kvmInfo[kvmID]['occupy'][msg['cpu']] #lock for multi-thread
            perf_param = msg['param']

            print "KVM pid {}, occupy {}, param {}".format(pid, occupy, perf_param)

            # data for control information which needs to notify the client
            data = ""

            # check whether the requested Vcpu or the VM has already been monitored
            if not occupy:
                kvmInfo[kvmID]['occupy'][msg['cpu']] = True

                ps = sub.perf_struct(pid, perf_param)
                intQueue = multiprocessing.Queue()

                # start the perf tool
                ps.perf_stat_start()

                # p1 read the real-time performance data to put it into a queue
                p1= multiprocessing.Process(target=ps.perf_stat_interval, args=(intQueue,))
                p1.start()

                # p2 reports the performance data to guest-client
                p2 = multiprocessing.Process(target=sender, args=(intQueue, self.request,))
                p2.start()

                print " waiting for perf end signal"
                cmd = self.request.recv(1024).strip()

                # get the "end" signal sent by the client
                print cmd

                # terminate both p1 and p2
                p1.terminate()

                # terminate the tool perf
                ps.perf_stat_stop(intQueue)

                kvmInfo[kvmID]['occupy'][msg['cpu']] = False


                # after the tool perf receives the stop signal,
                # it may generate some additional messages during its terminating process.
                # we buffer these messages into queue
                # sleep one second to get all the data delivered
                sleep (1)
                p2.terminate()



            else:
                data= "pmu is occupied, wait and retry"


            print "close connection"

            if len(data) > 0:
                print data
                self.request.sendall(data)

            sleep(1)
            self.request.close()



        except KeyboardInterrupt:
            print "keyboard interrupt, close connection"
            self.request.close()

        except Queue.Empty:
            pass

if __name__ == "__main__":

    try:
        # HOST, PORT = "193.168.122.0", 9995


        print "Start the server..."
        # Create the server, binding to the ip and the port
        SocketServer.TCPServer.allow_reuse_address = True
        server = SocketServer.ThreadingTCPServer((HOST, PORT), MyTCPHandler)

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
    except socket.error as (errno, string):
        print("Error " + repr(errno) + ": " + string)
        exit(0)
    except KeyboardInterrupt:
        print "keyboard interrupt, shutdown server"
        server.server_close()
        exit(0)
    except Exception as e:
        print(e)
