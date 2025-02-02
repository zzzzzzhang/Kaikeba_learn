# coding: utf-8

import torch.nn as nn
import torch.nn.functional as F

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3,3,3)
        self.maxpool1 = nn.MaxPool2d(kernel_size= 2)
        self.relu1 = nn.ReLU(inplace= True)
        
        self.conv2 = nn.Conv2d(3,6,3)
        self.maxpool2 = nn.MaxPool2d(kernel_size= 2)
        self.relu2 = nn.ReLU(inplace= True)
        
        self.fc1 = nn.Linear(6 * 30 * 30, 150)
        self.relu3 = nn.ReLU(inplace= True)
        
        self.drop = nn.Dropout(p = 0.5)
        self.fc2 = nn.Linear(150,3)
        self.softmax = nn.Softmax(dim = 1)
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.maxpool1(x)
        x = self.relu1(x)
        
        x = self.conv2(x)
        x = self.maxpool2(x)
        x = self.relu2(x)
        
        x = x.view(-1, 6 * 30 * 30)
        
        x = self.fc1(x)
        x = self.relu3(x)
        x = self.drop(x)
        
        x = self.fc2(x)
        x_class = self.softmax(x)
        
        return x_class

