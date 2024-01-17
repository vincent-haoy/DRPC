class Retraining_notifier:
    def __init___(self,size=10,threshold=0.9):
        self.size = size
        self.reward_history = np.zeros(size)
        self.threshold = threshold
        self.cnt = 0
        self.ready == False
    
    def store(self,reward):
        self.reward_history[self.size%self.cnt] = reward
        self.cnt += 1
    
    def require_retrain(self):
        return np.mean(self.reward_hisory) < self.threshold and self.cnt >= self.size