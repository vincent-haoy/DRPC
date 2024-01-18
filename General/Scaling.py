import os
from subprocess import PIPE, run
import re
import argparse
import json
def out(command):
    result = run(command,stdout=PIPE, universal_newlines= True, shell =True)
    return result.stdout

def getResourcePath(pod_name):    
    uid = out(f"sudo crictl pods --name {pod_name}").split("\n")
    if len(uid)< 2:
        print("the pod might no run on this machine")
        return "The pod might no run on this machine"
    
    
    uid = uid[1].split("  ")[0]
    jsonobject = json.loads(out(f"sudo crictl inspectp {uid}"))
    parent_path =jsonobject["info"]["config"]["linux"]["cgroup_parent"]
    temp_conju = jsonobject["info"]["runtimeSpec"]["linux"]["cgroupsPath"].split(":")
    child_path = temp_conju[1] + "-" + temp_conju[2]+".scope"

    Resources_mangement_path = "/sys/fs/cgroup" + parent_path + "/" + child_path
    return Resources_mangement_path

def cpu_scal(dividor, Resources_mangement_path, denominator=100000):
    """
    Utilization = divider / denominator
    """
    dividor = min(dividor,denominator)
    os.system(f"echo {str(dividor)} {str(denominator)} > " + Resources_mangement_path + "/cpu.max")
    print(f"the current cpu utilization is {str(dividor/denominator)} ")

def cpu_reset(Resources_mangement_path):
    with open(Resources_mangement_path + "/cpu.max", 'w') as f:
        f.seek(0)
        f.write("max")
        f.truncate()
    print("The cpu_limit has been reseted to 100%")


def reset_memory(Resources_management_path):

    with open(Resources_management_path + "/memory.min", 'w') as f:
        f.seek(0)
        f.write("0")
        f.truncate()
   
    with open(Resources_management_path + "/memory.low", 'w+') as f:
        f.seek(0)
        f.write("0")
        f.truncate()
    print("the memory threshold has been reset")

def memory_scal(amount, Resources_management_path):
    with open(Resources_management_path + "/memory.min", 'w') as f:
        f.seek(0)
        f.write(str(amount))
        f.truncate()
   
    with open(Resources_management_path + "/memory.low", 'w+') as f:
        f.seek(0)
        f.write(str(amount))
        f.truncate()
    print(f"the memory_min and memory_low had been set to {amount}")


if __name__ == "__main__":
    #Adding necessary input arguments
    parser = argparse.ArgumentParser(description='scaling')
    parser.add_argument('--pod',default="", type=str,help ='pod_name')
    parser.add_argument('--type',default="cpu", type=str,help ='cpu / memory')
    parser.add_argument('--amount',default="reset", type=str,help ='utilization: input an int;\n reset : input reset')   
    args = parser.parse_args()
    Resources_management_path = getResourcePath(args.pod)
    if args.type == "cpu":
        if args.amount == "reset":
            cpu_reset(Resources_management_path)
        else:
            cpu_scal(int(args.amount),Resources_management_path)
    elif args.type == "memory":
        if args.amount == "reset":
            reset_memory(Resources_management_path)
        else:
            memory_scal(args.amount, Resources_management_path)
    else:
        print("only memory and cpu scaling are avaliable")
        exit(0)
