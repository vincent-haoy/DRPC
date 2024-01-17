from torch.utils.data import Dataset, DataLoader
from torch.utils.data import DataLoader

class DeploymentBuffer:
    def __init__(self, max_size=10, state_size=5, action_size=3, number_of_deployments=32):
        self.mem_size = max_size
        self.state_size = state_size
        self.action_size = action_size
        self.number_of_deployments = number_of_deployments
        self.mem_cnt = 0
        self.memory = [np.zeros((max_size,state_size+action_size)) for i in range(number_of_deployments)]
    
    def remember(self, actions, env, request, predicted_req):
        deployment_states = list(env.deployment_states.values())
        allocated_states = list(env.pod_status.current_status.values())
        result_holder = []
        for i,depolyment_state in zip(range(self.number_of_deployments),deployment_states):
            # depoyment states
            test = [deployment_states[i][0],deployment_states[i][1],allocated_states[i][0],request,predicted_req,actions[i*3],actions[i*3+1],actions[i*3+2]]
            self.memory[i][self.mem_cnt % self.mem_size] = test
        self.mem_cnt += 1