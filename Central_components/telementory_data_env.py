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
LOCUST_CSV_PATH = "YOUR.csv"
PATH_PREFIX = "YOUR.csv"
class Telementory_Train_ticket:
  def __init__(self, max_replicas=5):
    initial_cpu = 500 * 100000
    initial_memory = 2000
    self.max_replicas = max_replicas
    self.init_dict = collections.OrderedDict(
      {
                           #'ts-consign-price-service': [1, initial_cpu, initial_memory],
                           #'ts-station-food-service': [1, initial_cpu, initial_memory],
                           #'ts-voucher-service': [1, initial_cpu, initial_memory],
                           #'ts-wait-order-service': [1, initial_cpu, initial_memory],
                           #'rabbitmq': [1, initial_cpu, initial_memory],
                           #'ts-admin-order-service': [1, initial_cpu, initial_memory],
                           #'ts-auth-service': [1, initial_cpu, initial_memory],
                           #'ts-avatar-service': [1, initial_cpu, initial_memory],
                           #'ts-consign-service': [1, initial_cpu, initial_memory],
                           #
                           #'ts-food-delivery-service': [1, initial_cpu, initial_memory],
                           #'ts-news-service': [1, initial_cpu, initial_memory],
                           #'ts-notification-service': [1, initial_cpu, initial_memory],
                           #'ts-ticket-office-service': [1, initial_cpu, initial_memory],
                           #'ts-train-food-service': [1, initial_cpu, initial_memory],


                           #######################################################
                           #'ts-admin-basic-info-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-admin-route-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-admin-travel-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-admin-user-service': [max_replicas, initial_cpu, initial_memory], 
                           #'ts-basic-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-config-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-delivery-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-execute-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-gateway-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-inside-payment-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-order-other-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-order-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-payment-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-preserve-other-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-preserve-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-price-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-rebook-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-route-plan-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-route-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-security-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-station-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-train-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-travel-plan-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-travel-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-travel2-service': [max_replicas, initial_cpu, initial_memory],
                           #'ts-ui-dashboard': [max_replicas, initial_cpu, initial_memory],
                           #'ts-user-service': [max_replicas, initial_cpu, initial_memory],
                           ##########################################################
                          
                          #'ts-seat-service': [max_replicas, initial_cpu, initial_memory],
                          #'ts-verification-code-service': [max_replicas, initial_cpu, initial_memory],
                          #'ts-contacts-service': [max_replicas, initial_cpu, initial_memory],
                          #'ts-cancel-service': [max_replicas, initial_cpu, initial_memory],
                          #'ts-assurance-service': [max_replicas, initial_cpu, initial_memory], 
                          #'ts-food-service': [max_replicas, initial_cpu, initial_memory],
                           ##########################################################
                          })

    self.deployments = list(self.init_dict.keys())
    self.deployments_number = len(self.deployments)
    self.current_status = deepcopy(self.init_dict)
    self.deployments_pod_dict = self.get_deployment_dict()
    self.pod_status = self.get_pod_status()
  
  def get_deployment_dict(self):
    deployment_pod_dict = collections.OrderedDict()
    for deployment in self.deployments:
        deployment_pods = [res[0] for res in  get_pod_by_selector(deployment)]
        deployment_pod_dict[deployment] = deployment_pods
    return deployment_pod_dict
  def get_pod_status(self):
    with open("pod_sta.csv",newline = '') as csvfile:
      pod_status_dict = collections.OrderedDict()
      lines = reader = csv.reader(csvfile)
      for line in lines:
        podname = line[0]
        podcpu = float(line[1])
        podmemory = float(line[2])
        pod_status_dict[podname] = [podcpu,podmemory]
      return pod_status_dict



class TelementoryEnv:
  def __init__(self, pod_initial_status = Telementory_Train_ticket()):
      self.max_replicates = pod_initial_status.max_replicas
      self.cpumax = 0.75
      self.memorymax = 0.75
      self.rtmax = 400
      self.cpulimit =  500 * 100000
      self.memory_limit = 2000

      self.observationspace = 5
      self.pod_status = pod_initial_status
      self.actionspace = len(pod_initial_status.current_status) * 3
      self.deployment_states = None
      self.cpu_utilization = None
      self.memory_utilization = None
      self.reward = None
      self.violate = False
  

  def telemetory_step(self,action_):
    action_ = action_.tolist()
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
        self.pod_status.current_status[target_deployment][0] = update
    
    if action >= 3 and action < 6:
      update = available_cpu_actions[action-3]  + current_cpu
      print(target_deployment, "cpu", update)
      if not (update <= 0 or update > 500 * 100000 or available_cpu_actions[action-3] == 0):
        self.pod_status.current_status[target_deployment][1] = update
    
    if action >= 6 and action < 9:
      update = available_memory_actions[action-6]  + current_memory
      print(target_deployment, "memory", update)
      if not (update <= 0 or update > 2000 or  available_memory_actions[action-6] == 0):
        self.pod_status.current_status[target_deployment][2] = update
    self.telementory_get_stat()

  def telementory_get_reward(self):
    if self.violate:
      return -1
    return self.reward
  def telementory_reset(self):
    self.telementory_get_stat()
  def telementory_get_stat(self):
    Rult = 1
    RUNNINGDEP = 1
    ultility_per_deployment = collections.OrderedDict()
    pod_status = self.pod_status.pod_status
    total_cpu_usage, total_memory_usage = 0, 0
    total_allocated_cpu, total_allocated_memory = 0, 0
    for deployments, pods in self.pod_status.deployments_pod_dict.items():
      #allocations
      allocated_cpu = self.pod_status.current_status[deployments][0] * self.pod_status.current_status[deployments][1]
      allocated_memory = self.pod_status.current_status[deployments][0] * self.pod_status.current_status[deployments][2]
      total_allocated_cpu += allocated_cpu
      total_allocated_memory += allocated_memory


      #usage
      cpu_usage = sum([pod_status[pod][0] for pod in pods])* 100000
      memory_usage = sum([pod_status[pod][1] for pod in pods]) * self.pod_status.current_status[deployments][0]/5
      Rult += (abs(self.cpumax-cpu_usage/allocated_cpu) + abs(self.memorymax - memory_usage/allocated_memory)) / (2 * RUNNINGDEP)
      total_memory_usage += memory_usage
      total_cpu_usage += cpu_usage
      ultility_per_deployment[deployments] = (cpu_usage / allocated_cpu,
                                    memory_usage/allocated_memory,
                                    self.pod_status.current_status[deployments][0],
                                    self.pod_status.init_dict[deployments][0],
                                    cpu_usage,
                                    allocated_cpu,
                                    memory_usage,
                                    allocated_memory)

    #self.cpu_utilization = total_cpu_usage/total_allocated_cpu
    #self.memory_utilization = total_memory_usage/total_allocated_memory
    self.cpu_utilization = self.pod_status.current_status[deployments][1]/(600 * 100000)
    self.memory_utilization = self.pod_status.current_status[deployments][2]/3000
    self.replicas_utilization = self.pod_status.current_status['ts-food-service'][0]/5
    Rult =((abs(0.75 - (total_cpu_usage/total_allocated_cpu))**2 + abs(0.75 - (total_memory_usage/total_allocated_memory)**2)) / 2 + 1)
    print(f"cpu = {total_cpu_usage}, allocated_cpou = {total_allocated_cpu}, memory = {total_memory_usage}, allocated_memory = {total_allocated_memory}")
    print(f"cpu usage = {total_cpu_usage/total_allocated_cpu}, memory_ usage = {total_memory_usage/total_allocated_memory}")
    self.reward = 1/(Rult)
    self.deployment_states = ultility_per_deployment

  def get_telementory_state(self):
    if self.violate:
      return[-1,-1,-1,-1,-1]
    return [0.58, 0.58, self.cpu_utilization, self.memory_utilization, self.replicas_utilization]
  def continue_step(self,action_):

    action1 = []
    #seperate the action into number_of_replicates, cpu, and memory for each deployment
    for i in range(0,len(action_),3):
      action1.append([action_[i],action_[i+1],action_[i+2]])
    
    # apply the actions
    for action2, (dep, _) in zip(action1, self.pod_status.current_status.items()):

      #actions are the output of the neural network between 0 and 1
      replicates = round( normalization(action2[0]))
      cpu =  normalization(action2[1]) *  5 * 100000
      memory =  normalization(action2[2]) * 10
      self.pod_status.current_status[dep][0] += replicates
      self.pod_status.current_status[dep][1] += cpu
      self.pod_status.current_status[dep][2] += memory
      print("diffent: ", replicates, cpu , memory)
      #print(self.pod_status.current_status[dep][0], self.pod_status.current_status[dep][1], self.pod_status.current_status[dep][2])
      if self.pod_status.current_status[dep][0] <= 0 or self.pod_status.current_status[dep][0] >= 6 or\
        self.pod_status.current_status[dep][1] < 10 * 100000 or self.pod_status.current_status[dep][1] > 600 * 100000 or\
        self.pod_status.current_status[dep][2] < 400 or self.pod_status.current_status[dep][2] > 3000:
        self.violate = True
      else:
        self.violate = False
        self.telementory_get_stat()


def normalization(action):
    s_power = 0
    if ( np.abs(action) > 0.5):
        direction = np.sign(action)
        s_power = np.clip(np.abs(action), 0.5, 1.0)
        s_power = direction * s_power
    return s_power