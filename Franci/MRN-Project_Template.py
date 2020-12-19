import numpy as np
import pandas as pd
from datetime import date
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
'''
Authors: 
Andrea Pimpinella <andrea.pimpinella@polimi.it>,
Alessandro E. C. Redondi <alessandroenrico.redondi@polimi.it>
Antonio Capone  <alessandroenrico.redondi@polimi.it>

This code preprocesses raw data to observe the impact of Covid19 pandemic on cellular networks.
'''
#--------------------------------
# IMPORT DATA
#--------------------------------

# Use this Section to import the data files provided in the project folder.

# NETWORK KPI
# Choose the geographic location (i.e. Milan) and the reference month (either January, February or March):

# PUT YOUR OWN FILE PATH!
file_path = '/Users/andreapimpinella/Desktop/MRN_2020_Covid19/MRN Project Deliverable/Data/Pkl_Files/'

# Cells KPIs
data = pd.read_pickle(file_path+'Milano_800_January_MRN.pkl')


# Cells Location:
locations = pd.read_pickle(file_path+'Coordinates_MILANO.pkl')

# For reference about python pandas data structure, look at:
# https://pandas.pydata.org

# This section shows some information regarding the dataset
print(20*'*')
print('Data types:\n')
print(data.dtypes)
print(20*'*')
print('Number of data points: ', len(data))
print('Number of columns in the dataset: ', len(data.columns))
print(20*'*')
print('Number of (distinct) cells: ', len(data.drop_duplicates(subset='ECELL_ID')))

#--------------------------------
# PRE-PROCESS DATA
#--------------------------------

#********************************
# Usually, it is interesting to recognize weekly trends in network related KPIs. The idea is to compare, for the
# considered KPIs, a typical weekly trend (i.e. in our case, before Covid-19 outbreak)
#cwith that one happening after the reference phenomenon (i.e., in our case, the Covid-19 outbreak).
# In this section, the second week of January (Monday 12th - Sunday 20th January 2020)
#is extracted from raw data, conditioning on the field "Date":

# January
week_three = data[data['Date'] < pd.Timestamp(year=2020, month=1, day=20, hour = 0, minute =1)]
week_three = week_three[week_three['Date'] > pd.Timestamp(year=2020, month=1, day=12, hour = 23, minute =59)]

#********************************

#********************************
# Typically, daily and night KPIs traces are analysed differently, as network users
# show very different behaviours depending on the two moments.
#In this section, the first week data are grouped into Daily (from 6AM to 24 PM)
# and Night (from 00 AM to 6 AM) Data

# January
week_three_day = week_three.set_index('Date').between_time('06:00:00', '23:59:59')
week_three_night = week_three.set_index('Date').between_time('00:00:00', '05:59:59')
#********************************

#********************************
# Raw data are provided as hourly samples, but it might be intereseting to consider also under-sampled
# versions of the data. For instance, it is possible to resample the dataset to obtain daily aggregation of KPIs.
# E.g. in this section the KPI reporting the average number of connected users ('USERNUM_AVG') is considered
# for a particular cell ID ('360767189319c367c8a7b4cf84a32a7841b3678f') and related data are aggregated to produce
# several Daily statistics for :

cell_id = 'c945addeee641c3b7e7098fe8cad5defe032223c' # this is a city center cell
ref_KPI = 'DL_VOL' # KPI to analyse: DL_VOl is expressed in bits
temp = week_three_day.loc[week_three_day['ECELL_ID']==cell_id,[ref_KPI]] # reference data

# Extract Statistics
median = temp.resample('D').agg({ref_KPI: np.median})
avg = temp.resample('D').agg({ref_KPI: np.mean})
std = temp.resample('D').agg({ref_KPI: np.std})

daily_stat = pd.DataFrame(index=median.index, columns = ['Median','Average','Standard_Deviaiton'])

daily_stat.Median = median.values
daily_stat.Average = avg.values
daily_stat.Standard_Deviaiton = std.values
#********************************
#********************************

#--------------------------------
#DATA VISUALIZATION
#--------------------------------
#********************************
# This section plots the average/median daily number of connected users to the cell taken as example

# open new figure
fig, ax = plt.subplots(figsize=(15,8))

# plot data
ax.plot(list(range(1,len(daily_stat)+1)),daily_stat['Average'], linestyle='--', lw=2, color='b',label='Average Trace', alpha=.8)
ax.plot(list(range(1,len(daily_stat)+1)),daily_stat['Median'], linestyle='--', lw=2, color='r',label='Median Trace', alpha=.8)


# Set plotting option
plt.xticks(color='black')
plt.yticks(color='black')
plt.grid(1)
plt.xticks(ticks = range(1,len(daily_stat)+1) ,labels = list(daily_stat.index.date), fontsize = 14, rotation=45)
plt.xlabel('Day of 2nd Week', color='black', fontsize=14)
plt.ylabel('Bits', color='black', fontsize=14)
plt.legend(loc="lower right", fontsize=14)
plt.title('Median Daily/Night Traces of '+ref_KPI+' - Cell_id:%s'%cell_id, fontsize=14)
plt.show(block=False)
figure_name = 'Median Daily Traces of '+ref_KPI+' - Cell Id: '+cell_id
plt.savefig(figure_name)
#********************************

#********************************
# This section plots the Median hourly number of connected users to the cell taken as example

# Sort hourly samples by date
ref = week_three.set_index('ECELL_ID').sort_values('Date').loc[cell_id,['Date',ref_KPI]]

# open new figure
fig, ax = plt.subplots(figsize=(15,8))

# plot data
ax.plot(list(range(0,len(ref))),ref[ref_KPI], linestyle='--', lw=2, color='b', alpha=.8)

# Set plotting options
plt.xticks(color='black')
plt.yticks(color='black')
plt.grid(1)
ticks_label = ref.reset_index().set_index('Date').sort_values(by='Date').index
ticks = [0, 12, 24, 36, 48, 60, 72, 83, 95, 107, 119, 131, 143, 155, 167] # indexes of 00.00 and 12.00 timestamps
#of each week day
plt.xticks(ticks = ticks,labels = ticks_label[ticks],fontsize = 14)
plt.setp( ax.xaxis.get_majorticklabels(), rotation=-45, ha="left", rotation_mode="anchor")
plt.xlabel('Day of 1st Week', color='black', fontsize=14)
plt.ylabel('Bits', color='black', fontsize=14) # unit of measure depends on the considered KPI
plt.title('Median Hourly Trace of'+ref_KPI+' - Cell Id: %s'%cell_id, fontsize=14)
plt.show(block=False)
figure_name = 'Median Hourly Traces of '+ref_KPI+' - Cell Id: '+cell_id
plt.savefig(figure_name)
#********************************

#********************************
# This section makes a box plot of the daily statistics regarding the number of connected
# users to the cell taken as example. For each day, the following statistics are extracted from the considered
# KPI:
# - Median Value
# - 25th and 75th Quantiles
# - Max and Min values

# For reference about how to read a box plot go here:
# https://towardsdatascience.com/understanding-boxplots-5e2df7bcbd51

# open new figure
fig, ax = plt.subplots(figsize=(15, 8))

# Create temporary variables

ref = temp.reset_index()
days = list(np.unique(ref['Date'].dt.day))
xtick = list(range(len(days)))

# For each day of the week, make the box plot of the corresponding hourly trace
for day in days:
    series = ref[ref['Date'].dt.day == day]

    ax.boxplot(series[ref_KPI], positions=[xtick[days.index(day)]])

# Set plotting options
plt.xticks(color='black')
plt.yticks(color='black')
plt.grid(1)
plt.xticks(ticks=xtick, labels=list(np.unique(ref.set_index('Date').index.date)), fontsize=14)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=-45, ha="left", rotation_mode="anchor")
plt.xlabel('Day of Week', color='black', fontsize=14)
plt.ylabel('Bits', color='black', fontsize=14)
plt.title('Box Plot of Median Daily '+ref_KPI+' - Cell Id: %s' % cell_id, fontsize=14)
figure_name = 'Box Plot of Median Daily'+ref_KPI+' - Cell Id: '+cell_id
plt.show(block=False)
plt.savefig(figure_name)
#********************************

#--------------------------------

