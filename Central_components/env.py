from StateCollector import *
from Locust_reader import *
import csv
import collections
import time
from copy import deepcopy
from local_server import *
import _thread
import multiprocessing
import math
import numpy as np
from statistics import mean
from multiprocessing import Pool
from run_load_test import *
import math
LOCUST_CSV_PATH = "your.csv"
PATH_PREFIX = "your_prefix/"
class Train_ticket:
  def __init__(self, max_replicas=5):
    initial_cpu = 100 * 100000
    initial_memory = 1000
    self.max_replicas = max_replicas
    self.init_dict = collections.OrderedDict(
      {
                           'ts-consign-price-service': [1, initial_cpu, initial_memory],
                           'ts-station-food-service': [1, initial_cpu, initial_memory],
                           'ts-voucher-service': [1, initial_cpu, initial_memory],
                           'ts-wait-order-service': [1, initial_cpu, initial_memory],
                           'rabbitmq': [1, initial_cpu, initial_memory],
                           'ts-admin-order-service': [1, initial_cpu, initial_memory],
                           'ts-auth-service': [1, initial_cpu, initial_memory],
                           'ts-avatar-service': [1, initial_cpu, initial_memory],
                           'ts-consign-service': [1, initial_cpu, initial_memory],
                           
                           #'ts-food-delivery-service': [1, initial_cpu, initial_memory],
                           #'ts-news-service': [1, initial_cpu, initial_memory],
                           #'ts-notification-service': [1, initial_cpu, initial_memory],
                           #'ts-ticket-office-service': [1, initial_cpu, initial_memory],
                           #'ts-train-food-service': [1, initial_cpu, initial_memory],


                           #######################################################
                           'ts-admin-basic-info-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-admin-route-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-admin-travel-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-admin-user-service': [max_replicas, initial_cpu, initial_memory], 
                           'ts-basic-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-config-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-delivery-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-execute-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-gateway-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-inside-payment-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-order-other-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-order-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-payment-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-preserve-other-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-preserve-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-price-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-rebook-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-route-plan-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-route-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-security-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-station-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-train-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-travel-plan-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-travel-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-travel2-service': [max_replicas, initial_cpu, initial_memory],
                           'ts-ui-dashboard': [max_replicas, initial_cpu, initial_memory],
                           'ts-user-service': [max_replicas, initial_cpu, initial_memory],
                           ##########################################################
                          'ts-seat-service': [max_replicas, initial_cpu, initial_memory],
                          'ts-verification-code-service': [max_replicas, initial_cpu, initial_memory],
                          'ts-contacts-service': [max_replicas, initial_cpu, initial_memory],
                          'ts-cancel-service': [max_replicas, initial_cpu, initial_memory],
                          'ts-assurance-service': [max_replicas, initial_cpu, initial_memory], 
                          'ts-food-service': [max_replicas, initial_cpu, initial_memory],
                           ##########################################################
                          })

    self.deployments = list(self.init_dict.keys())
    self.deployments_number = len(self.deployments)
    self.current_status = deepcopy(self.init_dict)
    self.deployments_pod_dict = self.get_deployment_dict()
  
  def get_deployment_dict(self):
    deployment_pod_dict = collections.OrderedDict()
    for deployment in self.deployments:
        deployment_pods = [res[0] for res in  get_pod_by_selector(deployment)]
        deployment_pod_dict[deployment] = deployment_pods
    return deployment_pod_dict
           
class SystemEnv:
  def __init__(self, requestCsv = "your.csv",namespace = "yournamespace", pod_initial_status = Train_ticket()):
      self.max_replicates = pod_initial_status.max_replicas
      self.cpumax = 0.75
      self.memorymax = 0.75
      self.rtmax = 400
      self.cpulimit =  500 * 100000
      self.memory_limit = 2000
      self.namespace= namespace
      self.observationspace = 5
      filename = open(requestCsv, 'r')
      self.pretrained = np.load("pretrained.npy")
      self.requests = []
      file = csv.DictReader(filename)
      for request in file:
        self.requests.append((int(request["request"]),int(request["predicted_request"])))
      
      
      self.total_request = len(self.requests)
      self.iterator = self.total_request

      
      self.pod_status = pod_initial_status
      self.actionspace = len(pod_initial_status.current_status) * 9
      self.deployment_states = None


  def get_state(self):
     # current change
    current_request = self.requests[self.iterator % self.total_request][0]
    predicted_request = self.requests[self.iterator % self.total_request][1]
    return [current_request/1000, predicted_request/1000, self.cpu_usage, self.memory_usage, self.qos["99%"]/1000]
  
  def get_deployment_states(self):
    return self.deployment_states
    
  def get_reward(self):
    rt = self.qos["99%"]
    Rqos = 1 if rt < self.rtmax  else  math.exp(-((rt-self.rtmax)/self.rtmax)**2)

    cpu_reward, memory_reward = 1, 1
    for k,v in self.deployment_states.items():
      cpu_reward += (abs(v[0] - self.cpumax))/self.pod_status.deployments_number
      memory_reward += (abs(v[1] - self.memorymax))/self.pod_status.deployments_number
      Rult = (cpu_reward + memory_reward)/2

    return Rqos/Rult
  
  def get_statistic2(self):
    current_request = self.requests[self.iterator % self.total_request][0]
    queue = multiprocessing.Queue()
    sub_process2 = multiprocessing.Process(target=run_locust, kwargs={"load": current_request, "pathprefix" : PATH_PREFIX })
    sub_process1 = multiprocessing.Process(target=top_pod, kwargs={"queue":queue})
    sub_process2.start()
    sub_process1.start()
    
    
    
    pod_usage = queue.get()
    sub_process2.join()
    sub_process1.join()
    allocated_cpu_resources, allocated_memory_resources = 0, 0
    used_cpu_resources, used_memory_resources = 0, 0
    ultility_per_deployment = collections.OrderedDict()
    for k,v in self.pod_status.current_status.items():
      replicas = self.pod_status.init_dict[k][0]
      #zero division handling for no avalible pod
      allocated_deployment_cpu_resources = 0.0001 + v[1] * v[0]
      allocated_deployment_memory_resources = 0.0001 + v[2] * v[0]
      allocated_memory_resources += allocated_deployment_memory_resources
      allocated_cpu_resources += allocated_deployment_cpu_resources
      
      deployment_cpu_usage = 0
      deployment_memory_usage = 0
      for pod, machine in get_pod_by_selector(k):
        #some of the pods might to be ready so fast, exclude them when doing the calculation
        deployment_cpu_usage += pod_usage[pod][0] * 100000
        deployment_memory_usage += pod_usage[pod][1] * self.pod_status.current_status[k][0]/self.pod_status.init_dict[k][0] 
      used_cpu_resources += deployment_cpu_usage
      used_memory_resources += deployment_memory_usage
      #The depolyment ultilities
      ultility_per_deployment[k] = (deployment_cpu_usage / allocated_deployment_cpu_resources,
                                    deployment_memory_usage/allocated_deployment_memory_resources,
                                    self.pod_status.current_status[k][0],
                                    self.pod_status.init_dict[k][0],
                                    deployment_cpu_usage,
                                    allocated_deployment_cpu_resources,
                                    deployment_memory_usage,
                                    allocated_deployment_memory_resources)
      #The overall pod ultilities
      
      
    
    self.cpu_usage = used_cpu_resources / allocated_cpu_resources
    self.memory_usage = used_memory_resources / allocated_memory_resources
    self.qos = get_qos(LOCUST_CSV_PATH)
    self.deployment_states = ultility_per_deployment
  
  def get_statistic(self):
    current_request = self.requests[self.iterator % self.total_request][0]
    queue = multiprocessing.Queue()
    sub_process2 = multiprocessing.Process(target=run_locust, kwargs={"load": current_request, "pathprefix" : PATH_PREFIX })
    sub_process1 = multiprocessing.Process(target=get_node_cpu_and_memory_usage, kwargs={"namespace": "yournamespace", "queue":queue})
    sub_process1.start()
    sub_process2.start()
    
    sub_process1.join()
    sub_process2.join()
    values = queue.get()
    # utilization
    self.cpu_usage = values[0]
    self.memory_usage = values[1]
    # qos
    self.qos = get_qos(LOCUST_CSV_PATH)
    
       
  def reset(self):
    self.pod_status = Train_ticket()
    # reset horizontal scaling 
    scaling_batch = []
    for (dep, ultilities) in self.pod_status.init_dict.items():
      #print(dep)
      #reset horizontal scaling
      #scaling_batch.append((dep,1, 1, self.max_replicates))
      horizontal_scaling(dep, 4, self.namespace)
      #block_pods_by_deployment(dep,1)
    #batch_scaling(scaling_batch)
    #print("the pods have been reset")
    
    time.sleep(10)
    #self.get_statistic2()
  
  def pretrained_reward(self):
    rtmax = 400
    cpumax = 0.75
    memorymax = 0.75
    rt = 300
    Rcpu = abs(cpumax-self.cpu_usage)**2
    Rmemory = abs(memorymax-self.memory_usage)**2
    Rqos = 1
    Rult = (Rcpu + Rmemory) / 2 + 1
    return Rqos/Rult
  
  def pretrained_state(self):
    current_request = self.requests[self.iterator % self.total_request][0]
    predicted_request = self.requests[self.iterator % self.total_request][1]
    return [current_request, predicted_request, self.cpu_usage, self.memory_usage, 300]
  
  def pretrained_getsat(self):
    deploymen_status = self.pretrained[self.iterator % self.total_request]
    total_cpu_usage, total_memory_usage = 0, 0
    allocated_cpu_usage, allocated_memory_usage = 0, 0
    g = 0
    for k,v in self.pod_status.current_status.items():
      total_cpu_usage += deploymen_status[g][0] * v[0]/self.pod_status.init_dict[k][0]
      total_memory_usage += deploymen_status[g][1] * v[0]/self.pod_status.init_dict[k][0]
      allocated_cpu_usage += v[0] * v[1]
      allocated_memory_usage += v[0] * v[2]
      g += 1
    self.cpu_usage = total_cpu_usage/allocated_cpu_usage
    self.memory_usage = total_memory_usage/allocated_memory_usage

    

  
  def pretrained_step(self, action_):
    self.iterator += 1
    action1 = []
    for i in range(0,len(action_),3):
      action1.append([action_[i],action_[i+1],action_[i+2]])
    
    # apply the actions
    deployment_batch = []
    for action2, (dep, _) in zip(action1, self.pod_status.current_status.items()):

      #actions are the output of the neural network between 0 and 1
      replicates = max(1, round(action2[0] * self.max_replicates))
      cpu = action2[1] *  self.pod_status.init_dict[dep][1]
      memory = action2[2] * self.pod_status.init_dict[dep][2]
      self.pod_status.current_status[dep][0],self.pod_status.current_status[dep][1],self.pod_status.current_status[dep][2] = replicates, cpu, memory
    self.pretrained_getsat()
      

  def step(self,action_):
    action_ = action_.tolist()
    self.iterator += 1
    cpu_action_step = 10*100000
    memory_step= 50

    available_replicas_actions = [0, 1, -1]
    available_cpu_actions = [0, cpu_action_step, -cpu_action_step]
    available_memory_actions = [0, memory_step, -memory_step]
    max_action = max(action_)
    max_index = action_.index(max_action)
    
    # 9 * 32
    deployment = max_index // 9
    action = max_index % 9
    target_deployment = self.pod_status.deployments[deployment]
    scaling_batch = []
    #horizontal scaling

    current_replicas = self.pod_status.current_status[target_deployment][0]
    current_cpu = self.pod_status.current_status[target_deployment][1]
    current_memory = self.pod_status.current_status[target_deployment][2]


    if action < 3:
      update = available_replicas_actions[action] + current_replicas
      print(target_deployment, "replicates", update)
      if not (update <= 1 or update >=5 or available_replicas_actions[action] == 0):
        self.pod_status.current_status[target_deployment][0] += available_replicas_actions[action]
        scaling_batch.append((target_deployment, current_cpu, current_memory, update))
    
    if action >= 3 and action < 6:
      update = available_cpu_actions[action-3]  + current_cpu
      print(target_deployment, "cpu", update)
      if not (update <= 0 or update > 500 * 100000 or available_cpu_actions[action-3] == 0):
        self.pod_status.current_status[target_deployment][1] = update
        scaling_batch.append((target_deployment, update, current_memory ,current_replicas))

    
    if action >= 6 and action < 9:
      update = available_memory_actions[action-6]  + current_memory
      print(target_deployment, "memory", update)
      if not (update <= 0 or update > 2000 or  available_memory_actions[action-6] == 0):
        self.pod_status.current_status[target_deployment][2] = update
        scaling_batch.append((target_deployment, current_cpu, update ,current_replicas))
  
    if len(scaling_batch) > 0:
        batch_scaling(scaling_batch)
    self.get_statistic2()

#state = SystemEnv()
#state.reset()