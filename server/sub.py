__author__ = 'Shaoteng Liu'

"""
This module configures and controls the performance monitoring tool perf.

__init__(): configure the tool perf.

perf_stat_start(Queue): start the tool perf

perf_stat_interval (Queue): sample the real time performance data and put it into a queue


perf_stat_stop(Queue): terminates the tool perf



"""



import subprocess
import sys
from time import sleep
import signal
#import psutil
import os
import sys

import multiprocessing

import Queue


class perf_struct:


    def __init__(self, pid, params):
        self.pid = pid
        self.params = params

    """
    configure and start the tool perf
    """
    def perf_stat_start(self):
        try:

            # a temp file for data buffering purpose (depreciated)
            # fileName = str(self.pid)+".log"
            # self.fileName = fileName
            #
            # self.log_file = open(fileName, 'w')

            # configure the tool perf
            cmd = "perf stat -p "+str(self.pid)+ self.params
            print(cmd)

            # start the tool perf
            p = subprocess.Popen(cmd.split(), stderr=subprocess.STDOUT, stdout=subprocess.PIPE)


            self.p = p

        except:
            print ("perf command does not start correctly")
            sys.exit(0)


    """
    get the real time performance data
    """
    def perf_stat_interval (self, intQueue):

        while (self.p.returncode == None):
            # get the real time performance data
            line=self.p.stdout.readline()
            # put the real time performance data into a queue
            intQueue.put(line)

    """
    terminate the tool perf
    """
    def perf_stat_stop(self, intQueue):
        try:
            if self.p:
                # send the terminate signal
                self.p.send_signal(signal.SIGINT)
                # get the data during the terminating process
                self.p.stdout.flush()
                out, err = self.p.communicate()
                # put the data into a queue
                intQueue.put(out)


                # for line in out.splitlines():
                #     print line
                #     intQueue.put(line)


                # self.log_file.write(out)
                #
                # self.log_file.flush()
                # self.log_file.close()


                print ("finishing")

            else:
                print (" start perf first")
        except:
            print ("perf command does not stop correctly")

"""
a  function for self testing purpose
"""
def funcB(intQueue):
    try:
        while(1):
            print intQueue.get(True, 2)
    except Queue.Empty:
        pass

if __name__=='__main__':
    #log_file = open("19319.log", 'w')
    ps=perf_struct(3730,  ' -I 500')
    ps.perf_stat_start()
    sleep(1)

    intQueue = multiprocessing.Queue()

    # producer
    p1= multiprocessing.Process(target=ps.perf_stat_interval, args=(intQueue,))
    p1.start()

    # consumer
    p2 = multiprocessing.Process(target=funcB, args=(intQueue,))
    p2.start()

    sleep(10)
    p1.terminate()
    sleep(1)
    p2.terminate()

    ps.perf_stat_stop(intQueue)
