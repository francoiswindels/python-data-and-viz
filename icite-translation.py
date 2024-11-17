# -*- coding: utf-8 -*-
"""
# quarterly PMID for each institute is in pubmed/animation

use this website to get the approximate potential translation
https://icite.od.nih.gov/analysis

Pubmed Entrez field elements documentation
https://www.nlm.nih.gov/bsd/mms/medlineelements.html#pt



Created on Fri Apr 12 15:03:52 2024
@author: uqfwinde
"""

import pandas as pd
import csv
import time
from datetime import datetime
import glob
import requests
from statistics import median
from statistics import mean
import re

t = time.time()

# import institute specific csv from animation
path = "../pubmed/animation"
files = glob.glob(path + "/*.csv") 

df = pd.DataFrame() 
content = [] # list of dataframe

for filename in files: 
    # reading content of csv file 
    # content.append(filename) 
    temp = pd.read_csv(filename, index_col=None) 
    content.append(temp)
# converting content to data frame 
df = pd.concat(content) 
# remove some institute
remCol = ['TRI', 'Crick', 'Pasteur', 'Broad', 'Riken', 'Hutchinson', 'MCRI' ]
df = df[~df['aff'].isin(remCol)]
df.reset_index(drop=True, inplace = True)

# remove all letters from endDate
df['endDate'] = df['endDate'].str.replace('\D', '', regex=True)
# datatypes
df['endDate'] = pd.to_datetime(df['endDate'])    
df['apt'] = '' # approximate potential translation
df['medApt'] = '' # median apt
df['meanApt'] = '' # mean apt
print(f'Total number of row to process {len(df)}')
print(f'Total number of publication to process {df.nbPub.sum()}')
t2 = time.time()
for idx, row in df.iterrows():
    t1 = time.time()
    temp = (((row.PMID).replace('[[','')).replace(']]',''))
    temp = (temp.replace('[','').replace(']',''))
    temp = temp.replace("'",'').replace(" ","")
    response = requests.get(f"https://icite.od.nih.gov/api/pubs?pmids={temp}")   
    pub = response.json()
    #a = [pub['data'][0]['apt']]
    locList = []
    for i in pub['data']:
        locList.append(i.get('apt'))
    # get the median of locList
    df.at[idx,'medApt'] = median(locList)
    df.at[idx,'meanApt'] = mean(locList)
    df.iat[idx, df.columns.get_loc('apt')] = locList
     
    time.sleep(0.2) # Sleep for 0.x seconds, slow down access
    print(f'reaching row Nb {idx} for {row.aff} took {time.time()-t1:.2f} sec; loop started {time.time()-t2:.2f} sec ago')

df.to_csv('../output/institute-apt-quarterly.csv')
print(f' Script executed in {time.time() - t}')
