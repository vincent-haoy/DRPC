def decision_maker_make_Decision(env, request, predicted_req, deployment_decision_makers):
    deployment_states = list(env.deployment_states.values())
    allocated_states = list(env.pod_status.current_status.values())
    all_results = T.tensor((), dtype=T.float)
    all_results = all_results.new_zeros((1, 3))
    for i,depolyment_state in zip(range(1),deployment_states):
        # depoyment states
        test = T.tensor([deployment_states[i][0],deployment_states[i][1],allocated_states[i][0],request,predicted_req])
        test = T.unsqueeze(test,0).to(T.float)
        all_results[i] = deployment_decision_makers[i].make_decision(test)
    return all_results.flatten().tolist()


# Initial data retrived
observation = env.get_state()
print(observation)
deploymentbuff_sta_reward = []
deploymentbuff_sta_usage = []
SAVECHECKPOINT = 10
print(env.deployment_states)
print(env.pod_status.current_status)
for episode in range(0, 10):
    action = agent.choose_action(observation, train=False)
    deploymentbuffer.remember(action, env, observation[0], observation[1])
    action_ = scale_action(action)
    env.step(action_)
    observation_, reward, done = env.get_state(), env.get_reward(), False
    observation = observation_
    deploymentbuff_sta_reward.append(reward)
    deploymentbuff_sta_usage.append(np.array([observation[2],observation[3]]))
    if episode % SAVECHECKPOINT== 0:
        average_observation = np.mean(np.array(deploymentbuff_sta_usage[-SAVECHECKPOINT:]),axis=0)
        avrage_reward = np.mean(deploymentbuff_sta_reward[-SAVECHECKPOINT:])
        print('Ep: {} AvgReward: {},observation: {}'.format(episode // SAVECHECKPOINT,avrage_reward, average_observation))

#distributed_system_making
deployment_decision_makers = [Deployment_decision_maker(deploymentbuffer.memory[i], 100) for i in range(32)]
for deployment_decision_maker in deployment_decision_makers:
    deployment_decision_maker.train(101)