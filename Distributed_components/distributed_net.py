class MLP(nn.Module):
    def __init__(self,input_dimension=5, output_dimension=3):
        super().__init__()
        self.layers = nn.Sequential(
          nn.Flatten(),
          nn.Linear(input_dimension, 20),
          nn.LayerNorm(20),
          nn.ReLU(),
          nn.Linear(20, 20),
          nn.Linear(20, 3),
          nn.Tanh()
        )
    def forward(self, x):
        return self.layers(x)

class MyDataset(Dataset):
    def __init__(self,data,cnt):
        self.data = T.from_numpy(data)
        self.cnt = cnt
 
    def __getitem__(self, index):
        x,y =self.data[index][0:5], self.data[index][5:]
        x = x.to(T.float)
        y = y.to(T.float)
        return x,y
 
    def __len__(self):
        return self.cnt

class Deployment_decision_maker:
    def __init__(self,memorybuffer,cnt):
        self.mlp = MLP()
        memorybuffer = memorybuffer[:cnt]
        self.loss_fn = nn.MSELoss()
        self.optimizer = T.optim.AdamW(self.mlp.parameters(), lr=1e-4)
        
        train_dataset = MyDataset(memorybuffer,cnt)
        self.train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers = 1, pin_memory = True)
    
    def train(self, epoch=1000):
        
        for g in range(epoch):
            current_loss = 0.0
            for i, (_input, _targets) in enumerate(self.train_loader):
                self.optimizer.zero_grad()
                outputs = self.mlp(_input)
                loss = self.loss_fn(outputs, _targets)
                print(loss,i)
                loss.backward()
                self.optimizer.step()
    def make_decision(self,state):
        return self.mlp.forward(state)