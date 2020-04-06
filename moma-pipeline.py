#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 21:58:55 2020

@author: ludivinelacour
"""

import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns

def acquisition():
    df=pd.read_csv('/Users/ludivinelacour/Documents/IRONHACK/data-cleaning/data/museum_modern_art.csv',sep=',')
    df=df.rename(columns={'Unnamed: 0':'Id'})
    
    return df

def drop_useless(df):
    null_col=df.isna().sum()
    null_col_percent=round(null_col[null_col>0]/df.shape[0]*100,2)
    
    drop_cols=null_col_percent[null_col_percent>50].index
    #Drop columns
    droped=df.drop(drop_cols,axis=1)
    
    return droped

def remove_duplicates(df):
    unique_rows=df.iloc[:,:].drop_duplicates()
    
    return unique_rows

def text_cleaning(df):
    parenthesis_col=['ArtistBio','Nationality','BeginDate','EndDate','Gender','Date']
    
    for col in parenthesis_col:
        df[col]=df[col].str.replace('\(','').str.replace('\)','')
        
    return df

def uniform_date(date):
    if re.search('[0-9]{4}$', date):
        return date[-4:]
    elif re.search('^[0-9]{4}', date):
        return date[:4]
    elif re.search('[0-9]{4}', date):
        pos = re.search('[0-9]{4}', date).start()
        return date[pos:pos+4]
    elif re.search('[0-9]{3}\?', date):
        new_date = re.sub('\?','0',date)
        pos = re.search('[0-9]{4}', new_date).start()
        return new_date[pos:pos+4]
    elif re.search('^[a-zA-Z \,\?\.]+$', date):
        return np.nan
    elif re.search('century',date):
        return date[0]+str('00')
    else:
        return date

def date_cleaning(df):
    # Convert in string type to work with regex
    df.Date=df.Date.astype(str)
    
    df.Date=df.Date.apply(uniform_date)
    
    # Manually cleaning some values
    cel=df[(df.Date=='November 10')&(df.Artist=='George Platt Lynes')]
    df.loc[cel.index,'Date']='1937'
    
    cel2=df[(df.Date=='newspaper published March 30')]
    df.loc[cel2.index,'Date']=np.nan
    
    return df

def getmean(x,mean_date):
    # x is a string
    if x in mean_date.index:
        return mean_date.loc[x]
    return

def guess_date_value(df):
    # Drop row with unknown artist and unknown date
    drop_row=df[(df.ConstituentID.isna())&(df.Date.isna())].index
    df.drop(drop_row,axis=0,inplace=True)
    
    # Find list of artist with only nan dates
    total_per_artist = df.ConstituentID.value_counts()
    number_nan_per_artist = df[df.Date.isna()].ConstituentID.value_counts()
    
    list_artist_nan_date=[]
    
    for a in number_nan_per_artist.iteritems():
        artist = a[0]
        number_of_nan = a[1]
        if total_per_artist.loc[artist] == number_of_nan:
            list_artist_nan_date.append(artist)
    # Keep rows excluding list of artist with only nan dates
    df=df[-df.ConstituentID.isin(list_artist_nan_date)]
    
    # Create a copy of dataframe and delete nan date to calculate the mean date of every artist
    df_bis=df.copy()
    null_date=df_bis.loc[df_bis.Date.isna()].index
    df_bis.drop(null_date,axis=0,inplace=True)
    
    # Convert date as int to work with mean
    df_bis.Date=df_bis.Date.astype(int)
    # Calculate mean for every artist
    mean_date=round(df_bis.groupby('ConstituentID')['Date'].agg('mean'))
    
    # Use of the function to return the mean of the constituentID
    df.Date=df.Date.fillna(df['ConstituentID'].apply(getmean,args=(mean_date,)))
    
    return df

def create_bins(df):
    # Convert all values as int to work on bins
    df.Date=df.Date.astype(int)
    
    labels=["690-1850"]
    cutoffs=[690]
         
    for i in range(1850,2020,10):
        cutoffs.append(i)
        labels.append(str(i+1)+"-"+str(i+10))
    # Manually append the last cut because
    cutoffs.append(2020)
    
    df['DateRange']=pd.cut(df.Date, cutoffs,labels=labels)
    
    return df

def create_viz(df):
    
    viz = pd.DataFrame(df.DateRange.value_counts()).reset_index()
    viz.columns=['DateRange','Count']
    
    sns.set()
    fig,ax=plt.subplots(figsize=(20,8))
    barchart=sns.barplot(data=viz,  x='DateRange',y='Count')
    plt.title("Repartition of art work by decade")
    
    return barchart

def save_viz(viz):
    fig=viz.get_figure()
    fig.savefig("/Users/ludivinelacour/Documents/IRONHACK/data-cleaning/output/repartition-of-art-work-by-decade.png")

if __name__=='__main__':
    data=acquisition()
    droped_col=drop_useless(data)
    removed_dup=remove_duplicates(droped_col)
    cleaned_txt=text_cleaning(removed_dup)
    cleaned_date=date_cleaning(cleaned_txt)
    filled_missing_date=guess_date_value(cleaned_date)
    final=create_bins(filled_missing_date)
    viz=create_viz(final)
    save_viz(viz)
    
    
    