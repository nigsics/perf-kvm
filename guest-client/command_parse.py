__author__ = 'lsteng'


"""
This module parses the command line of the guest client

"""




import argparse
import sys
import multiprocessing
import json

ncpu = multiprocessing.cpu_count()

ncpu_list=[]
n=0
for n in range(0, ncpu):
    ncpu_list.append(n)


ncpu_list.append(ncpu)

#print ncpu_list

"""
Parse the command line and return a dictionary

"""

def perf_parse():
    try:
        par = argparse.ArgumentParser(description='Processing perf guest_client command line', \
            prog='./guest_client.py', usage='%(prog)s [optional arguments]', \
                                    formatter_class=argparse.RawTextHelpFormatter
                )

        par.add_argument('-p', required=True, metavar='"program"', \
            help='set the program needs to monitor, \nexample: -p "ls -al" \n ')
        
        par.add_argument('-e', nargs='*', metavar='cache-misses cache-references cycles instructions branches branch-misses bus-cycles ref-cycles cpu-clock task-clock page-faults context-switches minor-faults major-faults alignment-faults emulation-faults dummy',\
            choices = ['cache-misses', 'cache-references', 'cycles', 'instructions', \
                    'branches', 'branch-misses', 'bus-cycles','ref-cycles', \
                    'cpu-clock', 'task-clock', 'page-faults', 'context-switches', \
                    'minor-faults', 'major-faults', 'alignment-faults','emulation-faults','dummy' 
            ], \
            help="choose which events to monitor \nexample: -e cache-misses cache-references\n ")
        par.add_argument('-i',  type=int, metavar='[ms]',\
         help='set the monitoring interval in millisecond \nexample: -i 500 \n ')
        par.add_argument('--cpu', default=0, choices = ncpu_list, type=int, \
            help="choose which cpu to monitor, 0 is all cpus, default=0 \nexample: --cpu 1\n ")
        par.add_argument('--host', default= '192.168.122.1', metavar='[IP_address]',\
            help = "set the host server IP address, default=192.168.122.1 \nexample: --host 192.168.122.1")
        par.add_argument('--port', nargs='?', default=9999, type=int, metavar='Port',\
            help="Set the port number of the server, default 9999 \nexample: --port 9999")


        arg = par.parse_args()
        mac = open('/sys/class/net/eth0/address').read().strip()

        
        perf_events = ""

        if arg.e:
            perf_events = ",".join(arg.e)
            perf_events = " -e " + perf_events

        perf_interval=""

        if arg.i :

            perf_interval = " -I " + str(arg.i)


        perf_param = perf_interval + perf_events
        # a command line is parsed into a dictionary structure
        msg = {'mac':mac, 'ip':arg.host, 'port':arg.port, 'cpu': arg.cpu, 'param': perf_param, 'program':arg.p}

        return msg

    except:
        sys.exit(0)



if __name__ == "__main__":

    msg =perf_parse()
    print msg