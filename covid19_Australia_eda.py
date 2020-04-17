# Exploratory data analysis of COCID-19 coronavirus deaths, cases and recoveries 15 Feb 2020
# See here for data source: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# The COVID-19 data are contained in three different csv files (confirmed, deaths and recoveries)
# THe idea is that we want to merge them into a single giant dataframe. We are only interested in Australian data!
# Make a dictionary called dataset with the keys as the csv files and the values being the appropriate columns
dataset = {'covid19_confirmed.csv': 'Confirmed', 'covid19_deaths.csv': 'Deaths', 'covid19_recovered.csv': 'Recovered'}

# Lets use a for loop to loop through the dictionary, make the necessary changes and create three seperate dataframes
df_list = []
for file, col_name in dataset.items():
    df = pd.read_csv(file)
    df = df.loc[df['Country/Region'] == 'Australia']  # Get only australian data!
    melt = df.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], var_name='date', value_name=col_name)  #Melt is used to change the individual date columns into a single date column for ease of plotting
    df_list.append(melt)

# You get three dataframes which I have named with the aus suffix
confirmed_aus, deaths_aus, recovery_aus = df_list

# I then merge the three dataframes into a single dataframe using the index and the province, date, latitude, longitude and country columns
confirm_deaths = confirmed_aus.merge(deaths_aus, on=['Province/State', 'Country/Region', 'Lat', 'Long', 'date'], how='inner')
combined_dataset = confirm_deaths.merge(recovery_aus, on=['Province/State', 'Country/Region', 'Lat', 'Long', 'date'], how='inner')

# Lets take care of the date column by setting it as an index (so we can plot it as a time series) and then removing any unwanted columns!
combined_dataset['date'] = pd.to_datetime(combined_dataset['date'], format='%m/%d/%y')  # Change the date column to datetime format (for ease of plotting) and then make it the index!
combined_dataset.index = combined_dataset['date']
combined_dataset.drop(columns=['Lat', 'Long', 'date'], inplace=True)  # remove unnecessary columns like Lat and Long and the duplicated date column (it is now in the index)

# Do some quick EDA to make sure everything is ok
print(combined_dataset.columns)  # Are all the column names correct?
print(combined_dataset.info())  # What are the data types of the columns?
print(combined_dataset.describe())  # Summary statistics for the different columns
print(combined_dataset.isnull().sum())  # Are there any null values?

# Do a quick check of the number of entries for missing dates(e.g. skipped dates).
from datetime import date
d0 = date(2020, 1, 22)
d1 = date(2020, 4, 15)
delta = d1 - d0
print('Number of days in our dataset: {}'. format(delta.days+1))
# We know that the dates in our dateset are between 2020-01-22 to 2020-04-15, and according to this formula,
# there are 85 days between our dates. There are 8 states (categories) in Australia so we expect a complete dataset
# (with no missing dates or data) to have 85*8 which is equal to 680. Exactly the number of rows that we get
# in our dataset (according to the df.info method)


# Not much happens before the 26 Jan so I am going to slice the data to be after the 26 Jan.
combined_dataset = combined_dataset.loc['2020-01-26':]

fig, ax = plt.subplots(3, 1, sharex='all', figsize=(15, 8))
sns.lineplot(x=combined_dataset.index, y='Confirmed', data=combined_dataset, hue='Province/State', ax=ax[0])
sns.lineplot(x=combined_dataset.index, y='Deaths', data=combined_dataset, hue='Province/State', ax=ax[1])
sns.lineplot(x=combined_dataset.index, y='Recovered', data=combined_dataset, hue='Province/State', ax=ax[2])
ax[1].get_legend().remove()
ax[2].get_legend().remove()
plt.xticks(rotation=45)
plt.show()
# You can see NSW is the worst affected state

# Here is a comparrison of the data for the two biggest states... NSW and Victoria
# First, make two new dataframes then do a plot!
combined_dataset_nsw = combined_dataset.loc[combined_dataset['Province/State'].isin(['New South Wales'])]
combined_dataset_vic = combined_dataset.loc[combined_dataset['Province/State'].isin(['Victoria'])]

# Then plot the confirmed cases, number of deaths and cases recovered in the same plot for NSW and victoria.
fig, ax = plt.subplots(2, 1, sharex='all', figsize=(15, 8))
combined_dataset_nsw.plot(y=['Confirmed', 'Deaths', 'Recovered'], color=['b', 'r', 'g'],
                          kind='line', title='NSW data', ax=ax[0])
combined_dataset_vic.plot(y=['Confirmed', 'Deaths', 'Recovered'], color=['b', 'r', 'g'],
                          kind='line', title='Victoria data', ax=ax[1])
ax[0].set_ylabel('Number of patients')
ax[1].set_ylabel('Number of patients')
plt.show()

# You can see that both NSW and Victoria show very similar trends
# I noticed that very few patients have recovered in NSW.
# I think this is due to the lack of reporting rather than any particular biological reason
