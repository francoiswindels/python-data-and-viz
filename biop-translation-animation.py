# -*- coding: utf-8 -*-
"""

retmax: Total number of records from the input set to be retrieved, up to a maximum of 10,000.

see https://biopython.org/  for details
main manual
https://biopython.org/DIST/docs/tutorial/Tutorial.html#chapter%3Aentrez

use this website to get the 
https://icite.od.nih.gov/analysis

Pubmed Entrez field elements documentation
https://www.nlm.nih.gov/bsd/mms/medlineelements.html#pt


in rec2list medline.records only keep the PT = ['Journal Article']
also remove the records with an SI containing 'ClinicalTrials.gov', keep track of number and reference

Created on Fri Apr 12 15:03:52 2024
@author: uqfwinde
"""

from Bio import Entrez
from Bio import Medline
import pandas as pd

import csv
import time
from datetime import datetime


t = time.time()

Entrez.api_key = "your API key goes here"  # provide API key to remove request limits
Entrez.email = "your email address goes here"  # good practice to provide contact details if needed
today = datetime.today().strftime('%Y-%m-%d')

quart = ['/01/01[Date - Publication]' , '/03/31[Date - Publication]', '/04/01[Date - Publication]' , '/06/30[Date - Publication]', 
         '/07/01[Date - Publication]', '/09/30[Date - Publication]' , '/10/01[Date - Publication]', '/12/31[Date - Publication]'] # n = 4

year = ['2000', '2001','2002','2003','2004','2005','2006','2007','2008','2009',
        '2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020',
        '2021','2022','2023','2024'] # n=25

# for each year create a searchdate by quarter, then loop thru each affiliation and add nb of pubmed and pubmedID to df
# first colummn will be date of quarter end, column for each affiliation 
# 4 quarter by 25 years for 17 affiliations, ~1700 API call
dfDate = pd.DataFrame()
dfDate['start']=''
dfDate['stop']=''
iterator = 0
for i, valYear in enumerate(year):
    for valQuart in quart:
        print(valQuart)
        if valQuart[4] == '0':
            dfDate.at[iterator,'start'] = valYear+valQuart
        else:    
            dfDate.at[iterator,'stop'] = valYear+valQuart
            iterator += 1    
df = pd.read_csv(r'../pubmed/ressource/translation-db.csv')
df = df[12:] # to get the last few institutes and not re-running the full script every time an error occurs
dfMerge = pd.DataFrame()
# we need one row per quarter/year and one column by affiliation, value in cell0/aff0 will be nb of publication, next column cell1/aff0 will be PMID as a list
for idx0, row0 in df.iterrows():
    # create temporary dataframe amd add empty column
    dfOut = pd.DataFrame()
    dfOut['aff'] = ''
    dfOut['endDate'] = ''
    dfOut['nbPub'] = ''
    dfOut['PMID'] = ''
    t1 = time.time()
    for idx1, row1 in dfDate.iterrows():
        # add endDate for row
        # assemble the searchkey
        #searchDate = ' (1980/01/01[Date - Publication] : 2024/10/30[Date - Publication])'  # features relevant for APT are stable 2 years after publication
        searchDate = f'{row1.start} : {row1.stop}'
        print(searchDate)
        searchKey = f'({row0.searchAff}) AND ({searchDate})'
        
     
        stream = Entrez.esearch(db="pubmed", term=searchKey, retmax=10000) # over long periods, for some Institute the number of citation goes beyond retmax
        # icite can only take 100000 PMID for a request
        record1 = Entrez.read(stream)
        stream.close()
        idlist = record1["IdList"]
        
        if len(idlist)>0:
            stream = Entrez.efetch(db="pubmed", id=idlist, rettype="medline", retmode="text")
            record2 = Medline.parse(stream)
            time.sleep(0.5) # Sleep for 0.5 seconds
            rec2List = list(record2)
            stream.close()
            dfOut.at[idx1,'aff'] = row0.searchName
            dfOut.at[idx1, 'endDate'] = row1.stop
            
            xxx = [item['PMID'] for item in rec2List]
            xxxx = list(map(lambda el:[el], xxx))
            dfOut.at[idx1,'nbPub'] = int(len(rec2List))
            dfOut.at[idx1,'PMID'] = xxxx
            #searchName = 'Riken'
    dfOut.to_csv(f'../animation/{row0.searchName}-pmid-quarterly.csv')
    print (f'script for {row0.searchName} took:  {time.time() - t1:.2f} seconds to run \n')

    dfMerge = pd.concat([dfMerge,dfOut], axis=0)
    print (f'sum of publication quarterly numbers: {dfOut.nbPub.sum()}')    
    #print (f'script for {row0.searchName} took:  {time.time() - t1} seconds to run \n')
#df.to_csv(f'../output/translation_db_{today}.csv')
dfMerge.to_csv('../output/institute-pmid-quarterly-20241104.csv')
print (f'overall run time for script for took:  {time.time() - t} seconds to run \n')
    
