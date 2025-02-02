
# coding: utf-8

# In[ ]:


import os
import matplotlib.pyplot as plt
from torch.utils.data import  DataLoader
import torch
from Network_Classes import *
from torchvision.transforms import transforms
from PIL import Image
import pandas as pd
import random
from torch import optim
from torch.optim import lr_scheduler
import copy


# In[ ]:


root_dir = 'F:/data/cv_learn/Dataset/'
train_dir = 'train/'
val_dir = 'val/'
train_anno = 'Classes_train_annotation.csv'
val_anno = 'Classes_val_annotation.csv'
classes = ['Mammals', 'Birds']
species = ['rabbits', 'chickens','rats']


# In[ ]:


class myDataset():
    '''
    用于获取图片数据
    '''
    def __init__(self, root_dir, annotations_file, transform= None):
        self.rootdir = root_dir
        self.annotations_file = annotations_file
        self.transform = transform
        
        if not os.path.isfile(self.annotations_file):
            print(self.annotations_file + 'does not exis!')
        
        self.file_info = pd.read_csv(annotations_file, index_col= None)
        self.size = len(self.file_info)
    
    def __call__(self):
        print('使用__getitem__(idx)获取图片数据')
    
    def __len__(self):
        return self.size
    
    def __getitem__(self, idx):
        '''
        定义了__getitem__魔法函数，该类就可以下标操作了：[]
        '''
        image_path = self.file_info['path'][idx]
        if not os.path.isfile(image_path):
            print(image_path + 'does not exis!')
            return None
        
        image = Image.open(image_path).convert('RGB')
        label_class = int(self.file_info['classes'][idx])
        label_species = int(self.file_info['species'][idx])
        sample = {'image': image, 'classes': label_class, 'species': label_species}
        
        if self.transform:
            sample['image'] = self.transform(image)
        
        return sample


# In[ ]:


#transforms:按顺序进行相应transform操作
train_tranfroms = transforms.Compose([transforms.Resize([128,128]),
                                      transforms.RandomHorizontalFlip(p = 0.5),
                                      transforms.ToTensor()
                                     ])
val_tranfroms = transforms.Compose([transforms.Resize([128,128]),
                                      transforms.ToTensor()
                                   ])
# 将数据路径实例化
train_dataset = myDataset(root_dir= root_dir + train_dir, 
                          annotations_file= train_anno, 
                          transform = train_tranfroms
                         )
val_dataset = myDataset(root_dir= root_dir + val_dir, 
                        annotations_file= val_anno, 
                        transform = val_tranfroms
                       )


# In[ ]:


# 转化为Dataloader
train_loader = DataLoader(dataset= train_dataset, batch_size= 128, shuffle= True)
val_loader = DataLoader(dataset= val_dataset)
data_loaders = {'train': train_loader, 'val': val_loader}


# In[ ]:


device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(device)


# In[ ]:


def visualize_trainDataset(idx):
    '''
    数据可视化
    '''
    print(len(train_dataset))
    #提取第idx个数据
    sample = train_loader.dataset[idx]
    #sample['image'] ：tensor of image 
    print(idx, sample['image'].shape, classes[sample['classes']], species[sample['species']])
    img = sample['image']
    plt.imshow(transforms.ToPILImage()(img))
    plt.show()
visualize_trainDataset(750)


# In[ ]:


def visualize_valDataset(idx):
    '''
    数据可视化
    '''
    print(len(val_dataset))
    #提取第idx个数据
    sample = val_loader.dataset[idx]
    #sample['image'] ：tensor of image 
    print(idx, sample['image'].shape, classes[sample['classes']], species[sample['species']])
    img = sample['image']
    plt.imshow(transforms.ToPILImage()(img))
    plt.show()
visualize_valDataset(46)


# In[ ]:


def train_model(model, data_loaders, criterion, optimizer, scheduler, num_epochs= 50):
    '''
    model: 需要训练的网络
    criterion：评价标准
    optimizer：优化器
    scheduler：学习率衰减
    num_epochs：迭代次数
    '''
    loss_list = {'train':[], 'val':[]}
    loss_list_classes = {'train':[], 'val':[]}
    loss_list_species = {'train':[], 'val':[]}
    
    accuracy_list = {'train':[], 'val':[]}
    accuracy_list_classes = {'train':[], 'val':[]}
    accuracy_list_species = {'train':[], 'val':[]}
    accuracy = {'accuracy_list':accuracy_list, 'accuracy_list_classes':accuracy_list_classes, 'accuracy_list_species':accuracy_list_species}
    #保存最好的模型与精度
    best_model_weights = copy.deepcopy(model.state_dict())
    best_acc = 0.0
    
    for epoch in range(num_epochs):
        print('Epoch{}/{}'.format(epoch + 1, num_epochs))
        print('-*' * 10)
        #每个epoch都需要进行一次训练与验证的过程
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()
            
            running_loss = 0.0
            running_loss_classes = 0.0
            running_loss_species = 0.0
            corrects_classes = 0
            corrects_species = 0
            
            for idx, data in enumerate(data_loaders[phase]):
                if phase == 'train':
                    print('training on batch {}'.format(idx))
                inputs = data['image'].to(device)
                labels_classes = data['classes'].to(device)
                labels_species = data['species'].to(device)
                #每个batch都需要重新计算梯度，所以清空
                optimizer.zero_grad()
                
                #只有在训练过程中需要反向传播，所以测试过程中可以set_grad_enabled(Flase)
                with torch.set_grad_enabled(phase == 'train'):
                    x_classes,x_species = model(inputs)
                    #得到的是classes和species的概率，需要继续转为类别
                    x_classes = x_classes.view(-1, 2)
                    x_species = x_species.view(-1, 3)
                    #preds_classes、species对应第几列的索引，即0还是1、2
                    _, preds_classes = torch.max(x_classes, 1)
                    _, preds_species = torch.max(x_species, 1)
                    #这里的 nn.CrossEntropyLoss()中第二个参数可以理解是groundtruth中‘1’的位置
                    #加权损失函数
                    criterion.weight = torch.tensor(data = [1,2],dtype= torch.float)
#                     criterion.weight = None
                    loss_classes = criterion(x_classes, labels_classes)
                    criterion.weight = None
                    loss_species = criterion(x_species, labels_species)
                    
                    loss = loss_classes + loss_species
                    
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()
                #loss.item() 返回一个value，乘以一个input.size，防止最后一组input数量不等
                running_loss += loss * inputs.size(0)
                running_loss_classes += loss_classes.item() * inputs.size(0)
                running_loss_species += loss_species.item() * inputs.size(0)
                #计算正确分类的个数
                corrects_classes += torch.sum(preds_classes == labels_classes)
                corrects_species += torch.sum(preds_species == labels_species)
            #求整个batch的loss&记录不同loss
            loss_list[phase].append(running_loss/len(data_loaders[phase].dataset))
            loss_list_classes[phase].append(running_loss_classes/len(data_loaders[phase].dataset))
            loss_list_species[phase].append(running_loss_species/len(data_loaders[phase].dataset))
            
            epoch_acc_classes = corrects_classes.double() / len(data_loaders[phase].dataset)
            epoch_acc_species = corrects_species.double() / len(data_loaders[phase].dataset)
            epoch_acc = (epoch_acc_classes + epoch_acc_species) * 0.5
            
            #乘以100应该是为了后面显示（）% ???
            accuracy_list[phase].append(100 * epoch_acc)
            accuracy_list_classes[phase].append(100 * epoch_acc_classes)
            accuracy_list_species[phase].append(100 * epoch_acc_species)
            #用测试集测试，记录最佳权值
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_weights = copy.deepcopy(model.state_dict())
                print('Best val classes Acc: {:.2%}'.format(best_acc))
        
        #学习率衰减
        exp_lr_scheduler.step()
    #合并loss、acc
    loss = {'loss_list' : loss_list, 'loss_list_classes' : loss_list_classes, 'loss_list_species':loss_list_species}
    accuracy = {'accuracy_list':accuracy_list, 'accuracy_list_classes':accuracy_list_classes, 'accuracy_list_species':accuracy_list_species}
    
    #保存模型
    model.load_state_dict(best_model_weights)
    torch.save(model.state_dict(),'Acc_{:04d}'.format(round(best_acc.item() * 100)))
    print('Best val classes Acc: {:.2%}'.format(best_acc))
    return model, loss, accuracy


# In[ ]:


network = Net().to(device)
optimizer = optim.SGD(network.parameters(), lr=0.01, momentum=0.9)
criterion = nn.CrossEntropyLoss()
#每步衰减至0.9 * 上步学习率
exp_lr_scheduler = lr_scheduler.StepLR(optimizer, step_size= 1, gamma= 0.9)
#训练网络
num_epochs = 100
model, loss_dict, accuracy_dict = train_model(network, 
                                              data_loaders, 
                                              criterion, 
                                              optimizer, 
                                              exp_lr_scheduler, 
                                              num_epochs= num_epochs)


# In[ ]:


def visualize_trainFig(task):
    '''
    phase: classes/species
    '''
    x = range(0, num_epochs)
    y1 = loss_dict['loss_list_{}'.format(task)]['train']
    y2 = loss_dict['loss_list_{}'.format(task)]['val']

    plt.plot(x, y1, color="r", linestyle="-", marker="o", linewidth=1, label="val")
    plt.plot(x, y2, color="b", linestyle="-", marker="o", linewidth=1, label="train")
    plt.legend()
    plt.title('{} loss vs epoches'.format(task))
    plt.ylabel('loss')
    plt.savefig("{} loss vs epoches.jpg".format(task))
    plt.show()
    plt.close('all') # 关闭图 0

    y3 = accuracy_dict['accuracy_list_{}'.format(task)]["train"]
    y4 = accuracy_dict['accuracy_list_{}'.format(task)]["val"]
    plt.plot(x, y3, color="r", linestyle="-", marker=".", linewidth=1, label="train")
    plt.plot(x, y4, color="b", linestyle="-", marker=".", linewidth=1, label="val")
    plt.legend()
    plt.title('train and val {}_acc vs epoches'.format(task))
    plt.ylabel('{}_accuracy'.format(task))
    plt.savefig("train and val {}_acc vs epoches.jpg".format(task))
    plt.show()
    plt.close('all')

visualize_trainFig('classes')
visualize_trainFig('species')


# In[ ]:


############################################ Visualization ###############################################
def visualize_model(model):
    model.eval()
    with torch.no_grad():
        for i, data in enumerate(data_loaders['val']):
            inputs = data['image']
            labels_classes = data['classes'].to(device)
            labels_species = data['species'].to(device)

            x_classes, x_species = model(inputs.to(device))
            x_classes = x_classes.view( -1,2)
            x_species = x_species.view( -1,3)
            _, preds_classes = torch.max(x_classes, 1)
            _, preds_species = torch.max(x_species, 1)
            print(species[preds_species])
            print(inputs.shape)
            plt.imshow(transforms.ToPILImage()(inputs.squeeze(0)))
            plt.title('predicted classes: {}\n ground-truth classes: {}\n                        predicted species: {}\n ground-truth species: {}'.format(classes[preds_classes], 
                                                                             classes[labels_classes], 
                                                                             species[preds_species],
                                                                             species[labels_species]))
            plt.show()

visualize_model(model)


# In[ ]:




