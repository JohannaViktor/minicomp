import pandas as pd
import numpy as np

def clean_store(df):
    df['Assortment'] = df['Assortment'].replace({"a": 1, "b": 2, "c": 3})
    #Fill missing values from CopetitionDistance with the Mode
    df.CompetitionDistance = df.CompetitionDistance.fillna(250)
    #Impute missing values
    df.CompetitionOpenSinceYear = df.CompetitionOpenSinceYear.fillna(2013)
    df.CompetitionOpenSinceMonth = df.CompetitionOpenSinceMonth.fillna(9)
    #Convert to integers
    
    df[['CompetitionOpenSinceMonth','CompetitionOpenSinceYear']] = df[['CompetitionOpenSinceMonth','CompetitionOpenSinceYear']] .astype(int)
    return df

def clean_train(train):
    '''Clean the data from the train set'''
    #Drop the rows where we do not have a store number
    #train = pd.read_csv("../minicomp-rossman/data/train.csv")
    train.loc[train['StateHoliday']==0,'StateHoliday'] = '0'
    train = train.dropna(subset=['Store'])
    #drop sales = 0
    train = train.loc[(train['Sales']!=0)]
    #Convert the store numbers from float to int
    train.loc[:, 'Store'] = train.loc[:, 'Store'].astype(int)
    #Convert the date colume to datetime
    train.loc[:, 'Date'] = pd.to_datetime(train.loc[:, 'Date'])
    #Convert the DayOfWeek column to Monday(0) - Sunday(6) and replace missing values 
    train.loc[:, 'DayOfWeek'] = train.loc[:, 'Date'].dt.dayofweek
    #Convert to a timestamp
    train["timestamp"] = train.Date.values.astype(np.int64)
    #Remove rows where we do not have a vale for sales or customers
    train = train[(train["Sales"].notna()) | (train["Customers"].notna())]
    return train

def customer_fill(train):
    null_mask = train.loc[:, 'Customers'].isnull()
    sub = train.loc[null_mask, :]
    sales_by = train.groupby(["Store","DayOfWeek"]).mean().reset_index()

    fill = []
    for row in range(sub.shape[0]):

        store = sub.iloc[row, :].loc['Store']
        day = sub.iloc[row, :].loc['DayOfWeek']

        mask = sales_by['Store'] == store
        store_only = sales_by.loc[mask, :]

        mask = store_only['DayOfWeek'] == day
        store_day = store_only.loc[mask, 'Customers']
        fill.append(store_day.values)

    train.loc[null_mask, 'Customers'] = np.array(fill)
    #train['Customers'] = train['Customers'].astype(int)
    
    return(train)

def sales_fill(train):
    '''Fill the sales columns which are null'''
    null_mask = train.loc[:, 'Sales'].isnull()
    
    sub = train.loc[null_mask, :]
    sales_by = train.groupby(["Store","DayOfWeek"]).mean().reset_index()

    fill = []
    for row in range(sub.shape[0]):

        store = sub.iloc[row, :].loc['Store']
        day = sub.iloc[row, :].loc['DayOfWeek']

        mask = sales_by['Store'] == store
        store_only = sales_by.loc[mask, :]

        mask = store_only['DayOfWeek'] == day
        store_day = store_only.loc[mask, 'Sales']
        fill.append(store_day.values)

    train.loc[null_mask, 'Sales'] = np.array(fill)
    #train['Sales'] = train['Sales'].astype(int)
    
    
    
    return(train)

def fill_fast(train_,col):
    #train_['test_h'] = 0
    train_['test_h'] = train_.groupby(['Store', 'DayOfWeek'])['Sales'].transform('mean')

    train_.loc[train_['Sales'].isna(),col] = train_['test_h']
    train_ = train_.dropna(subset=[col])
    train_ = train_.drop('test_h', axis = 1)
    return train_



def store_train_merge(df, train):
    #Merge the tables
    master = train.merge(df, left_on="Store", right_on="Store")
    
    return master