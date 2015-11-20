# perf-kvm
The perf-kvm is a tool for monitoring the performance of a KVM virtual machine. The tool can be used for the purpose of testing infrastructure compliance for running various VNFs. The main property of this tool is that it can monitor both hardware events as well as software events of a specific KVM-based virtual machine. 

The perf-kvm is consists of two parts:

  1. A server which needs to run on the host Linux machine. The python files for the server is in the folder "./server"

  2. A guest-client which needs to run in a guest KVM virtual machine requesting monitoring. The python files for the client is in the folder "./guest-client"

The server builds a dictionary for each VM running on the host machine, which contains information such as Name, MAC,  PID and PIDs of the vCPUs of a VM. Guest VMs can issue performance monitoring requests to the server through a client software. The server will configure the tool “perf” to monitor the hardware performance of the requesting VM. Then, the server will send the performance data back to the requesting VM.

For details on how to install and run the perf-kvm, please see usage.txt.

####Acknowledgement:
This code has been developed in the context of the Yardstick OPNFV project (https://wiki.opnfv.org/yardstick).
