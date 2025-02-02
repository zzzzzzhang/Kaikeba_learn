# coding: utf-8

import os
import pandas as pd
from PIL import Image 

roots = 'D:/cv_learn/projectI/Dataset/'
phase = ['train','val']
classes = ['Mammals', 'Birds']
species = ['rabbits', 'chickens']

dataIfo = {'train':{'path':[],'classes':[]},
           'val':{'path':[],'classes':[]}}

for p in phase:
    for s in species:
        data_dir = roots + p + '/' + s
        data_filenames = os.listdir(data_dir)
        for filename in data_filenames:
            imgPath = data_dir + '/' + filename
            try:
                img = Image.open(imgPath)
            except OSError:
                pass
            else:
                dataIfo[p]['path'].append(imgPath)
                dataIfo[p]['classes'].append(0 if s == 'rabbits' else 1)
    annotation = pd.DataFrame(dataIfo[p])
    annotation.to_csv('Classes_{}_annotation.csv'.format(p),index= None)
    print('Classes_{}_annotation is saved'.format(p))

