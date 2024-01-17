

def plot_learning_curve(episodes, records, title, ylabel,scale="1"):
    plt.figure()
    plt.plot(episodes, records, color='b', linestyle='-')
    plt.title(title)
    plt.xlabel('episode * '+ scale)
    plt.ylabel(ylabel)
 
    plt.show()


def scale_action(action, low=-1, high=1):
    action = np.clip(action, -1, 1)
    weight = (high - low) / 2
    bias = (high + low) / 2
    action_ = action * weight + bias
 
    return action_



#episodes = [i+1 for i in range(EPISODE)]
#plot_learning_curve(episodes, avg_reward_history, title='AvgReward', ylabel='reward')
import gym
env = System.env()
agent = TD3(alpha=0.0003, beta=0.0003, state_dim=env.observation_space.shape[0],
                action_dim=env.action_space.shape[0], actor_fc1_dim=400, actor_fc2_dim=300,
                critic_fc1_dim=400, critic_fc2_dim=300, ckpt_dir="here", gamma=0.99,
                tau=0.005, action_noise=0.1, policy_noise=0.2, policy_noise_clip=0.5,
                delay_time=2, max_size=1000000, batch_size=256)

    
max_episodes = 1000
total_reward_history = []
avg_reward_history = []
for episode in range(max_episodes):
        total_reward = 0
        done = False
        observation, info = env.reset()

        while not done:
            action = agent.choose_action(observation, train=True)
            action_ = scale_action(action, low=env.action_space.low, high=env.action_space.high)

            observation_, reward, done,truncated, info = env.step(action_)
            agent.remember(observation, action, reward, observation_, done)
            agent.learn()
            total_reward += reward
            observation = observation_
        total_reward_history.append(total_reward)
        avg_reward = np.mean(total_reward_history[-100:])
        avg_reward_history.append(avg_reward)
        print('Ep: {} Reward: {} AvgReward: {}'.format(episode+1, total_reward, avg_reward))


episodes = [i+1 for i in range(max_episodes)]
plot_learning_curve(episodes, avg_reward_history, title='AvgReward', ylabel='reward',
                        figure_file=args.figure_file)