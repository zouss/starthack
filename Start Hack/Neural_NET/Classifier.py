from torch import nn
import torch.nn.functional as F


class Classifier_(nn.Module):
    def __init__(self):
        super().__init__()
        # layers
        self.fc1 = nn.Linear(7, 10)
        self.fc2 = nn.Linear(10, 5)
        self.fc3 = nn.Linear(5, 2)

 
    def forward(self, x):
        #x = x.view(x.shape[0], -1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.log_softmax(self.fc3(x), dim=1)
        return x