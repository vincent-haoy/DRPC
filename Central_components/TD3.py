class TD3:
    def __init__(self, alpha, beta, state_dim, action_dim, actor_fc1_dim, actor_fc2_dim,
                 critic_fc1_dim, critic_fc2_dim, ckpt_dir, gamma=0.99, tau=0.005, action_noise=0.2,
                 policy_noise=0.2, policy_noise_clip=0.5, delay_time=2, max_size=1000000,
                 batch_size=256):
        self.gamma = gamma
        self.tau = tau
        self.action_noise = action_noise
        self.policy_noise = policy_noise
        self.policy_noise_clip = policy_noise_clip
        self.delay_time = delay_time
        self.update_time = 0
        self.checkpoint_dir = ckpt_dir
        self.action_dim = action_dim
 
        self.actor = ActorNetwork(alpha=alpha, state_dim=state_dim, action_dim=action_dim,
                                  fc1_dim=actor_fc1_dim, fc2_dim=actor_fc2_dim)
        self.critic1 = CriticNetwork(beta=beta, state_dim=state_dim, action_dim=action_dim,
                                     fc1_dim=critic_fc1_dim, fc2_dim=critic_fc2_dim)
        self.critic2 = CriticNetwork(beta=beta, state_dim=state_dim, action_dim=action_dim,
                                     fc1_dim=critic_fc1_dim, fc2_dim=critic_fc2_dim)
 
        self.target_actor = ActorNetwork(alpha=alpha, state_dim=state_dim, action_dim=action_dim,
                                         fc1_dim=actor_fc1_dim, fc2_dim=actor_fc2_dim)
        self.target_critic1 = CriticNetwork(beta=beta, state_dim=state_dim, action_dim=action_dim,
                                            fc1_dim=critic_fc1_dim, fc2_dim=critic_fc2_dim)
        self.target_critic2 = CriticNetwork(beta=beta, state_dim=state_dim, action_dim=action_dim,
                                            fc1_dim=critic_fc1_dim, fc2_dim=critic_fc2_dim)
 
        self.memory = ReplayBuffer(max_size=max_size, state_dim=state_dim, action_dim=action_dim,
                                   batch_size=batch_size)
 
        self.update_network_parameters(tau=1.0)
    def save_to_pth(self, prefix = "./checkpoint/", suffix=".pth"):
        self.actor.save_checkpoint(prefix + "actor" + suffix)
        self.target_actor.save_checkpoint(prefix + "target_actor" + suffix)
        
        self.critic1.save_checkpoint(prefix + "critic1" + suffix)
        self.critic2.save_checkpoint(prefix + "critic2" + suffix)
        
        self.target_critic1.save_checkpoint(prefix + "target_critic1" + suffix)
        self.target_critic2.save_checkpoint(prefix + "target_critic2" + suffix)
        
    def load_from_pth(self, prefix="./checkpoint/", suffix=".pth"):
        #["actor1, critic1", "critic2", "target_actor", "target_critic1", "target_critic2"]
        self.actor.load_checkpoint(prefix + "actor" + suffix)
        self.target_actor.load_checkpoint(prefix + "target_actor" + suffix)
        
        self.critic1.load_checkpointt(prefix + "critic1" + suffix)
        self.critic2.load_checkpoint(prefix + "critic2" + suffix)
        
        self.target_critic1.load_checkpoint(prefix + "target_critic1" + suffix)
        self.target_critic2.load_checkpoint(prefix + "target_critic2" + suffix)
        pass
            
 
    def update_network_parameters(self, tau=None):
        if tau is None:
            tau = self.tau
 
        for actor_params, target_actor_params in zip(self.actor.parameters(),
                                                     self.target_actor.parameters()):
            target_actor_params.data.copy_(tau * actor_params + (1 - tau) * target_actor_params)
 
        for critic1_params, target_critic1_params in zip(self.critic1.parameters(),
                                                         self.target_critic1.parameters()):
            target_critic1_params.data.copy_(tau * critic1_params + (1 - tau) * target_critic1_params)
 
        for critic2_params, target_critic2_params in zip(self.critic2.parameters(),
                                                         self.target_critic2.parameters()):
            target_critic2_params.data.copy_(tau * critic2_params + (1 - tau) * target_critic2_params)
 
    def remember(self, state, action, reward, state_, done):
        self.memory.store_transition(state, action, reward, state_, done)
 
    def choose_action(self, observation, train=True):
        self.actor.eval()
        state = T.tensor([observation], dtype=T.float).to(device)
        action = self.actor.forward(state)
 
        if train:
            # exploration noise
            noise = T.tensor(np.random.normal(loc=0.0, scale=self.action_noise,size=self.action_dim),
                              dtype=T.float).to(device)
            action = T.clamp(action+noise, -1, 1)
        self.actor.train()
 
        return action.squeeze().detach().cpu().numpy()
 
    def learn(self):
        if not self.memory.ready():
            return
 
        states, actions, rewards, states_, terminals = self.memory.sample_buffer()
        states_tensor = T.tensor(states, dtype=T.float).to(device)
        actions_tensor = T.tensor(actions, dtype=T.float).to(device)
        rewards_tensor = T.tensor(rewards, dtype=T.float).to(device)
        next_states_tensor = T.tensor(states_, dtype=T.float).to(device)
        terminals_tensor = T.tensor(terminals).to(device)
 
        with T.no_grad():
            next_actions_tensor = self.target_actor.forward(next_states_tensor)
            #action_noise = (T.randn_like(T.zeros(self.action_dim)) * self.policy_noise).to(device)
            #action_noise = T.tensor(np.random.normal(loc=0.0, scale=self.policy_noise, size=self.action_dim),
            #                        dtype=T.float)
            # smooth noise
            #action_noise = T.clamp(action_noise, -self.policy_noise_clip, self.policy_noise_clip)
            #next_actions_tensor = T.clamp(next_actions_tensor+action_noise, -1, 1)
            next_actions_tensor = T.clamp(next_actions_tensor, -1, 1)
            q1_ = self.target_critic1.forward(next_states_tensor, next_actions_tensor).view(-1)
            q2_ = self.target_critic2.forward(next_states_tensor, next_actions_tensor).view(-1)
            q1_[terminals_tensor] = 0.0
            q2_[terminals_tensor] = 0.0
            critic_val = T.min(q1_, q2_)
            target = rewards_tensor + self.gamma * critic_val
        q1 = self.critic1.forward(states_tensor, actions_tensor).view(-1)
        q2 = self.critic2.forward(states_tensor, actions_tensor).view(-1)
 
        critic1_loss = F.mse_loss(q1, target.detach())
        critic2_loss = F.mse_loss(q2, target.detach())
        critic_loss = critic1_loss + critic2_loss
        self.critic1.optimizer.zero_grad()
        self.critic2.optimizer.zero_grad()
        critic_loss.backward()
        self.critic1.optimizer.step()
        self.critic2.optimizer.step()
 
        self.update_time += 1
        if self.update_time % self.delay_time != 0:
            return
 
        new_actions_tensor = self.actor.forward(states_tensor)
        q1 = self.critic1.forward(states_tensor, new_actions_tensor)
        actor_loss = -T.mean(q1)
        self.actor.optimizer.zero_grad()
        actor_loss.backward()
        self.actor.optimizer.step()
 
        self.update_network_parameters()