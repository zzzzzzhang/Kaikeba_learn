# -*- coding: utf-8 -*-
"""make_anno.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ycXwHNWKHJtny7rJr4Ls-dhYOEKAJXlD
"""

# # 授权访问谷歌云盘
# !apt-get install -y -qq software-properties-common python-software-properties module-init-tools
# !add-apt-repository -y ppa:alessandro-strada/ppa 2>&1 > /dev/null
# !apt-get update -qq 2>&1 > /dev/null
# !apt-get -y install -qq google-drive-ocamlfuse fuse
# from google.colab import auth
# auth.authenticate_user()
# from oauth2client.client import GoogleCredentials
# creds = GoogleCredentials.get_application_default()
# import getpass
# !google-drive-ocamlfuse -headless -id={creds.client_id} -secret={creds.client_secret} < /dev/null 2>&1 | grep URL
# vcode = getpass.getpass()
# !echo {vcode} | google-drive-ocamlfuse -headless -id={creds.client_id} -secret={creds.client_secret}

# #建立根目录
# !mkdir -p drive
# !google-drive-ocamlfuse drive

import pandas as pd
import os
from PIL import Image
os.chdir('/content/drive/Colab Notebooks/project1_classification/Stage_2 Species_classification')

roots = '/content/drive/Colab Notebooks/project1_classification/Dataset/'
phase = ['train','val']
species = ['rabbits', 'rats', 'chickens']

dataInfo = {'train': {'path': [], 'species': []},
             'val': {'path': [], 'species': []}}

for p in phase:
  for s in species:
    DATA_DIR = roots + '/' + p + '/' + s
    DATA_NAME = os.listdir(DATA_DIR)

    for item in DATA_NAME:
      print(item)
      try:
        img = Image.open(os.path.join(DATA_DIR, item))
      except OSError:
        pass
      else:
        dataInfo[p]['path'].append(os.path.join(DATA_DIR, item))
        if s == 'rabbits':
            dataInfo[p]['species'].append(0)
        elif s == 'rats':
            dataInfo[p]['species'].append(1)
        else:
            dataInfo[p]['species'].append(2)

  ANNOTATION = pd.DataFrame(dataInfo[p])
  ANNOTATION.to_csv('Species_%s_annotation.csv' % p)
  print('Species_%s_annotation file is saved.' % p)















