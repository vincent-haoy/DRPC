import os
import paramiko
#https://stackoverflow.com/questions/52487333/how-to-assign-a-namespace-to-certain-nodes
"""nodes = []#your node list
#os.system("kubectl delete namespace your_namespace")
for node in nodes:
  #command = f"kubectl label node {node} experiment-"
  command = f"kubectl label node {node} env=trainticket"
  os.system(command)"""
#os.system("kubectl create namespace ?")

def init_scaling_file(passpharse, file="scaling.py", denstination = "your_namespace"):
    """
    Initialize a folder and copy the scaling file to the destination.
    This feature can be used for cgroup v1 but it is depreacted for cgroup v2.
    """

    nodes = []#your node list
    for node in nodes:
        #print("initializing node " + node)
        #ssh = paramiko.SSHClient()
        #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #ssh.connect(hostname=node, port=?, username=?, password="?")
        #print("connected")
        #stdin1, stdout1, stderr1 = ssh.exec_command('mkdir ?')
        #print("making dir done")
        
        #ssh.close()
        scpcommand = "sshpass -p " +passpharse +" scp  Scaling.py ?@"+node+":?"
        #print(scpcommand)
        os.system(scpcommand)

init_scaling_file("?")
#annotations:
#    scheduler.alpha.kubernetes.io/node-selector: "env=trainticket"
#make deploy Namespace=?
#make reset-deploy Namespace=?
#env=trainticket