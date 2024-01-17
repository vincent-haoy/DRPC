from kubernetes import client, config
import os
import subprocess
import time
import warnings
import paramiko
warnings.filterwarnings("ignore")

config.load_kube_config()
def get_node_cpu_and_memory_usage(namespace,queue=None):
    results = []
    for i in range(0,3):
        time.sleep(15)
        proc = subprocess.Popen([f"kubectl top nodes -n %{namespace}"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        outlines = out.decode("utf-8").split("\n")[1:-1]
        result = []
        for line in outlines:
            break_line = line.split("  ")
            break_line = [i.replace(" ","") for i in break_line if i !=" " and i != ""]
            nodename, cpu_usage, memory_usage = break_line[0], int(break_line[2].replace("%",""))/100, int(break_line[4].replace("%",""))/100
            result.append([nodename, cpu_usage, memory_usage])
        results.append(result)

    # the average cpu/memory usage per machine, you can return this for other purpose
    pooled_results = []
    cpu_total = 0
    memory_total = 0
    
    for l1,l2,l3 in zip(results[0], results[1], results[2]):
        name = l1[0]
        cpu_avg = (l1[1] + l2[1] + l3[1]) /3
        memory_avg = (l1[2] + l2[2] +l2[2])/3
        pooled_results.append([name, cpu_avg, memory_avg])
    # handling conneciton err
    if len(pooled_results) == 0:
        queue.put([-1,-1])
        return
    #the global average cpu/memory usage
    for pooled_result in pooled_results:
        cpu_total += pooled_result[1]
        memory_total += pooled_result[2]
    cpu_total /= len(pooled_results)
    memory_total /= len(pooled_results)

    queue.put([cpu_total,memory_total])
    return pooled_results

#print(get_cpu_and_memory_usage("haoyu"))




api_client = client.ApiClient()
v1 = client.CoreV1Api()


v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)
"""resutl = v1.list_node()

for i in ret.items:
    for j in i.spec.containers:
        if j.resources.requests or j.resources.limits:
            print(i.spec.node_name, j.name, j.resources)"""

"""api = client.CustomObjectsApi()
k8s_nodes = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
for stats in k8s_nodes['items']:
    print(stats)
    print("Node Name: %s\tCPU: %s\tMemory: %s" % (stats['metadata']['name'], stats['usage']['cpu'], stats['usage']['memory']))
    print("\n\n")"""


#get deployment
def get_deployment_with_replicates(namespace):
    """
    Get the deployment from a given namespace
    This will return a tuple with a format: (name, replicas. available replicates, unavailable_replicas)
    """
    apis_api = client.AppsV1Api()
    resp = apis_api.list_namespaced_deployment(namespace=namespace)
    deployment = []
    for i in resp.items:
        deployment.append((i.metadata.name,i.status.replicas,i.status.available_replicas, i.status.unavailable_replicas))
    return deployment

"""def vertical_scaling(podname, usage, namespace = "haoyu"):
    
    #only work for cgroup v2, implement cgroupv1 version if in required
    
    command =  "kubectl exec "+ podname + " -n "+ namespace + " -- cat /sys/fs/cgroup/cpu.max"
    os.system(f"kubectl exec {podname} -n {namespace} -- echo {str(usage)} 100000 > " + "/sys/fs/cgroup/cpu.max")
    os.system(command)
    print(command)"""
    
def batch_scaling(deployments, namespace = "haoyu"):
    scaling_group_by_nodes = {"cc167" :[], "cc182":[], "cc188":[],"cc193":[]}
    for (deployment, cpu, memory, portion) in deployments:
        cpu = max(1000, cpu*100000)#convert to the cgroup v2 unit
        memory = max(600, memory*2000)
        relavent_pod = get_pods_in_deployment(deployment, namespace)
        number_of_relavent_pod =  len(relavent_pod)
        replicates = max(1, portion)
        for i in range(replicates):
            pod, host = relavent_pod[i]
            scaling_group_by_nodes[host].append((pod,cpu,memory))

        for j in range (replicates,number_of_relavent_pod):
            pod, host = relavent_pod[j]
            scaling_group_by_nodes[host].append((pod,1000,10))
    for k, v in scaling_group_by_nodes.items():
        vertical_scaling_by_nodes(k,v)

    
def vertical_scaling_by_nodes(host, scaling_list,passpharse="tinker"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, port=22, username='root', password=passpharse)
    commands = ""
    for pod, cpu, memory in scaling_list:
        commands += f"python3 ~/haoyu/Scaling.py --pod {pod} --type cpu --amount {cpu}\n"
        commands += f"python3 ~/haoyu/Scaling.py --pod {pod} --type memory --amount {memory}\n"
    stdin1, stdout1, stderr1 = ssh.exec_command(commands)
    ssh.close()

    
#horizontal scaling 
def vertical_scaling(dep, types="cpu", usage=100000, namespace="haoyu", deployment = "deployment",portion = 1):
    relavent_pod = get_pods_in_deployment(dep, namespace)
    replicates = max(1, round(portion * len(relavent_pod)))
    done = 0
    for pod, host in relavent_pod:
        remote_vertical_scaling(host, pod, usage,types)
        done += 1
        if done == replicates:
            break
        

#remmote vertical scaling
def remote_vertical_scaling(host, pod, usage,target,passpharse="tinker"):
    #@Todo: caling the Scaling.py remotely
    print(host, pod)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, port=22, username='root', password=passpharse)
    command = f"python3 ~/haoyu/Scaling.py --pod {pod} --type {target} --amount {usage}"
    stdin1, stdout1, stderr1 = ssh.exec_command(command)
    print(stdout1.read())
    print(stderr1.read())
    ssh.close()

def block_pods_by_deployment(deployment,propotion):
    pods = get_pod_by_selector(deployment)
    number_of_pods = len(pods)
    noblock_pods = max(1, round(propotion * number_of_pods))
    for i in range(0,noblock_pods):
        unblock_pod_connection(pods[i][0])
    
    for j in range(noblock_pods, number_of_pods):
        block_pod_connection(pods[j][0])        


def block_pod_connection(pod_name,namespace="haoyu"):

    subprocess.run(["kubectl", "label", "pod", pod_name, "trafficblocked=blocked", "-n", namespace, "--overwrite"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    #out = os.system(command) # discard printing

def unblock_pod_connection(pod_name,namespace="haoyu"):
    subprocess.run(["kubectl", "label", "pod", pod_name, "trafficblocked=notblocked", "-n", namespace, "--overwrite"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    #out = os.system(command) # discard printing
    
    # you have to implement the network policy 

def horizontal_scaling(dep, replicates, namespace, deployment="deployment"):
    scaling_command = f"kubectl scale {deployment}/{dep} --replicas={replicates} -n {namespace}"
    os.system(scaling_command)
#prometheus-kube-state-metrics

#kubectl scale deployment/prometheus-kube-state-metrics --replicas=3
def get_pods(namespaces):
    """
    This will return all the pods for a given namespace
    """
    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod(namespaces)
    pods = []
    for pod in pod_list.items:
        print(pod.metadata.name)
        print(pod)
        break
        pods.append(pod.metadata.name)
    return pods

def Horizontal_applied(deployment_name,namespace):
    """
    Check if all the pods are in the "runing state"
    """
    call_back =  v1.list_namespaced_pod(namespace=namespace, label_selector='app={}'.format(deployment_name))
    for i in call_back.items:
        if i.status.phase != "Running":
            return False
    return True  

"""print(Horizontal_applied("haoyu"))
print(get_pods("haoyu"))
print(get_deployment_with_replicates("haoyu"))"""

def get_pods_in_deployment(deployment_name, namespace="haoyu"):
    call_back = v1.list_namespaced_pod(namespace=namespace, label_selector='app={}'.format(deployment_name))
    pods = []
    for pod in call_back.items:
        if pod.status.phase == "Running":
            pods.append((pod.metadata.name,pod.spec.node_name))
    return pods
#horizontal_scaling("rabbitmq", 1, "haoyu", deployment="deployment")
#print(get_pods_in_deployment("rabbitmq", "haoyu"))
#print(Horizontal_applied("rabbitmq", "haoyu"))


def top_pod(queue):
    #sleep 10 seconds for locust testing start
    time.sleep(27)
    topcmd=subprocess.run(["kubectl", "top" ,"pods", "-n", "haoyu"], capture_output=True,timeout=10)
    if topcmd.stdout:
        pod_usage_dict = dict()
        podusage =  topcmd.stdout.decode('utf-8')
        podusage = podusage.splitlines()
        lines = []
        for line in podusage[1:]:
            info = line.split()
            pod_usage_dict[info[0]] = (int(info[1].strip("m")), int(info[2].strip("Mi")))
        queue.put(pod_usage_dict)
        return pod_usage_dict
    
def get_pod_by_selector(selector,prefix="app=",namespace = "haoyu"):
    slecorcmd=subprocess.run(["kubectl", "get" ,"pods", "-n", namespace, "-l",prefix + selector, "-o","wide"], capture_output=True,timeout=10)
    if slecorcmd.stdout:
        podusage =  slecorcmd.stdout.decode('utf-8')
        podusage = podusage.splitlines()
        lines = []
        res = []
        for line in podusage[1:]:
            info = line.split()
            ready = info[1].split("/")
            if  ready[0] == ready[1] and info[2] != "Terminating" :
                res.append((info[0], info[6]))
        return res

