# -*- coding: utf-8 -*-
"""
update field type (numeric, string date)
pivot table to compatible shapre for anmimation

racing bar chart
try: https://pypi.org/project/bar-chart-race/
conda install -c conda-forge bar_chart_race

Created on Tue Oct 29 13:05:26 2024
@author: uqfwinde
"""

import pandas as pd
import bar_chart_race as bcr

df = pd.read_csv(r'../output/institute-apt-quarterly.csv')

# datatypes
df['endDate'] = pd.to_datetime(df['endDate'])

pivoted = pd.pivot_table(df, index = "endDate", columns = "aff", values="meanApt")
pivoted = pivoted.fillna(0)
pivoted = pivoted*100
# Removing last row (it is incomplete)
pivoted = pivoted.iloc[:-1]
# pivoted = pivoted.drop(columns=['TRI', 'Crick', 'Pasteur', 'Broad', 'Riken', 'Hutchinson', 'MCRI' ])
pivMed = pivoted.rolling(8).median()
pivMed = pivMed[10:]
pivSum = pivoted.cumsum()
bcr.bar_chart_race(df=pivMed, steps_per_period=30, period_length=1000, filename="../output/apt-anim.mp4")

