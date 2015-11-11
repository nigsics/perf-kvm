__author__ = 'Shaoteng Liu'

"""
This module gets the information about all the KVMs running on the host machine.
We assume that all the KVMs are managed by libvirt.
Thus, we can read the .xml files under /var/run/libvirt/qemu/
to get the information about all the running KVMs.

perfDict(): parse each individual xml file, and build a dictionary which contains
            the pid, mac information of each KVM


"""




# import subprocess
import os
import re
import glob
# from time import sleep


"""
parse each individual .xml file by using regular expressions, and build a dictionary which contains
the pid, mac information of each KVM.
"""

def perfDict():
    try:
        rootdir = "/var/run/libvirt/qemu/"
        # check wether the path for .xml files is correct
        if not glob.glob(rootdir + "*.xml") :
            errorMessage="*.xml files used for KVM configuration are not found under folder {}, please check the 'rootdir' variable in perf_dict.py".format(rootdir)
            raise IOError (2, errorMessage)

        dict = {}

        for root, subFolders, files in os.walk(rootdir):
            for file in files:
                #print file

                matchObj = re.search('xml', file, re.I)

                if matchObj:
                    pid = []
                    occ = []
                    #print file
                    with open(os.path.join(root, file), 'r') as fin:
                        for line in fin:
                            matchObj = re.search('pid=\'(\d+)\'', line, re.I)
                            if matchObj:
                                pid.append(matchObj.group(1))
                                occ.append(False)

                            matchObj = re.search('mac address=\'(.+)\'', line, re.I)

                            if matchObj:

                                mac = matchObj.group(1)
                    dict[mac] = {'pid': pid, 'occupy': occ}

        return dict
    except IOError as ioex:
        print 'errno:', ioex.errno
        print ioex
        exit(0)

if __name__=='__main__':
    print perfDict()
