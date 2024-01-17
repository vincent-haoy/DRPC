import os
import paramiko
#https://stackoverflow.com/questions/52487333/how-to-assign-a-namespace-to-certain-nodes
"""nodes = ['cc167', 'cc182', 'cc188', 'cc193', 'cc236','cc165']
#os.system("kubectl delete namespace haoyu")
for node in nodes:
  #command = f"kubectl label node {node} experiment-"
  command = f"kubectl label node {node} env=trainticket"
  os.system(command)"""
#os.system("kubectl create namespace haoyu")

def init_scaling_file(passpharse, file="scaling.py", denstination = "haoyu"):
    """
    Initialize a folder and copy the scaling file to the destination.
    This feature can be used for cgroup v1 but it is depreacted for cgroup v2.
    """

    nodes = ["cc167", "cc182", "cc188","cc193"]
    for node in nodes:
        #print("initializing node " + node)
        #ssh = paramiko.SSHClient()
        #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #ssh.connect(hostname=node, port=22, username='root', password=passpharse)
        #print("connected")
        #stdin1, stdout1, stderr1 = ssh.exec_command('mkdir haoyu')
        #print("making dir done")
        
        #ssh.close()
        scpcommand = "sshpass -p " +passpharse +" scp  Scaling.py root@"+node+":haoyu"
        #print(scpcommand)
        os.system(scpcommand)

init_scaling_file("tinker")
#annotations:
#    scheduler.alpha.kubernetes.io/node-selector: "env=trainticket"
#make deploy Namespace=haoyu
#make reset-deploy Namespace=haoyu
#env=trainticket