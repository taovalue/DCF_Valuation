# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 10:37:05 2019

@author: patrick.fang
https://www.linkedin.com/pulse/financial-screen-scraping-python-chris-hemphill/

Ingesting the Data to Feed the Model
So the web scraping begins here. We grab, clean, and manipulate the needed data with a popular library data scientists use for cleanup: pandas.

It's a big function, but what it's doing is simple.

- It pulls in a dictionary of stock ticker symbols paired with their brand names and categories.
- It then scans multiple places on the web for a particular stock and searches through those pages for needed data elements.
- Try replacing the curly brackets in the URLs with the 'AAPL' stock ticker and browsing to those pages on your own to get a sense for the data that it's reading

The pd.read_html() function stores the tables on an HTML page as a list of DataFrames, which explains the slicing notation [0] you see after the calls to those functions
The function goes through the process of finding, cleaning, and calculating DCF for each stock and displays a progress bar as it's downloading from the web.

It may look like a huge function, but that's the nature of having to pick and clean so many individual points from different locations.

"""

import pandas as pd #data processing
from tqdm import tqdm #progress bars
import numpy as np #numerical processing
import datetime #enable datetime manipulation
pd.set_option('max_columns', 500) #more columns makes it easier to work with wide datasets

import npv_fcf as npv

def trackr(stocks, margin_of_safety=.25, discount_rate=.1, growth_decline=.05, years=10, multiplier=12, yahoo_adjust=1000):
    '''trackr reads a dictionary of stocks and their associated 
    company names and categories and returns today's Yahoo Finance 
    stats on the corresponding stock as a row of values that can be appended to a dataframe'''
    
    #Error Handling
    if type(stocks) != dict:
        print('Error. You must enter these in a dictionary format, where the symbol is the key, \
        name is first list value, and the subsequent list values are categories')
        return
    
    tickers = list(stocks.keys()) #convert to list in case single string entered
    quotes = [] #capture each entry as a row
    
    for ticker in tqdm(tickers):
        '''Grab appropriate data based on tickers. This stores the appropriate URLs 
        and then pulls data from the pages of Yahoo Finance. This takes a while,
        so tqdm's progress bar is a great way to reduce anxiety!'''
        
        quote = 'https://finance.yahoo.com/quote/{}?p-{}'.format(ticker, ticker) #Quote string
        cashflow = 'https://finance.yahoo.com/quote/{}/cash-flow?p={}'.format(ticker, ticker) #Cashflow string
        stat = 'https://finance.yahoo.com/quote/{}/key-statistics?p={}'.format(ticker, ticker) #Key Statistics String
        balance = 'https://finance.yahoo.com/quote/{}/balance-sheet?p={}&.tsrc=fin-srch'.format(ticker, ticker) #Balance Sheet String
        analysis = 'https://finance.yahoo.com/quote/{}/analysis?p={}'.format(ticker, ticker) #Analysis String
        quote_data = pd.read_html(quote) #grab the data that YAHOO has on the given stock
        cashflow_data = pd.read_html(cashflow) #grab the cashflow statement
        stat_data = pd.read_html(stat) #grab key stats
        balance_data = pd.read_html(balance) #grab balance sheet
        analysis_data = pd.read_html(analysis) #grab analysis data

        '''The HTML tables parse into a list. It will take some cleanup to prepare the list for a dataframe
        stock 1 gives us Previous Close, Open, Bid, Ask, Day's Range, 52 Week Range, Volume, and Avg. Volume
        stock 2 gives us Market Cap, Beta (3Y Monthly), PE Ratio (TTM), EPS (TTM), 
        Earnings Date, Forward Dividend & Yield, Ex-Dividend Date, 1y Target Est'''

        stock1 = quote_data[0].transpose() #Transpose data into meaningful arrangement.
        stock1.columns = stock1.iloc[0] #set new header row
        stock1.drop(0, inplace=True) #drop the old

        stock2 = quote_data[1].transpose() #Transpose data into meaningful arrangement
        stock2.columns = stock2.iloc[0] #set new header row
        stock2.drop(0, inplace=True) #drop the old

        #combine them
        stock_cat = pd.concat([stock1, stock2], axis=1)
        
        #grab cashflow data for discounted cashflow calculation
        stock_cat['Cash Flow'] = np.where(cashflow_data[0].iloc[9][1] == '-', 
                                          cashflow_data[0].iloc[9][2],
                                          cashflow_data[0].iloc[9][1])
        stock_cat['CapEx'] = np.where(cashflow_data[0].iloc[11][1] == '-', 
                                          cashflow_data[0].iloc[11][2],
                                          cashflow_data[0].iloc[11][1])
        

        #add them up for Free Cash Flow calculation
        stock_cat['Free Cash Flow'] = int(stock_cat['Cash Flow']) + int(stock_cat['CapEx'])
        
        #Adds cash and cash equivalents with short term investments. #Discards blank values that yahoo returns and goes back a year if needed
        
        stock_cat['Cash On Hand'] = np.where(balance_data[0].iloc[2,1] == '-',
                                             int(balance_data[0].iloc[2,2]) + int(balance_data[0].iloc[3,2].replace('-', '0')),
                                             int(balance_data[0].iloc[2,1].replace('-', '0')) + \
                                             int(balance_data[0].iloc[3,1].replace('-', '0')))
        
        #grabs long term debt, filling in blank values where needed
        stock_cat['Long Term Debt'] = np.where(balance_data[0].iloc[21, 1] == '-',
                                               balance_data[0].iloc[21, 2],
                                               balance_data[0].iloc[21, 1])
        
        #Pulls Yahoo's version of shares outstanding, applying a different multiplier for billions vs millions
        stock_cat['Approx Shares Outstanding'] = np.where(stat_data[8].loc[2,1][-1] == 'B',
                                                          float(stat_data[8].loc[2,1][:-1]) * 1000000000,
                                                          float(stat_data[8].loc[2,1][:-1]) * 1000000)
        
        #pulls Yahoo's compiling of analyst 5 year estimate for growth then take a discount by margin of safety
        stock_cat['Conservative Analyst 5y'] = (float(analysis_data[5].loc\
                                                      [4, ticker.upper()].split('%')[0])/100)*(1-margin_of_safety)
        
        
        # turn columns to numeric
        num_cols = ['Cash Flow', 'Free Cash Flow', 'CapEx', 'Cash On Hand', 
                    'Long Term Debt', 'Approx Shares Outstanding', 
                    'Conservative Analyst 5y','Previous Close', 'Open', 'Volume', 'Avg. Volume', 
                    'Beta (3Y Monthly)', 'PE Ratio (TTM)', 'EPS (TTM)', '1y Target Est']
        
        for col in num_cols:
            stock_cat[col] = np.nan_to_num(pd.to_numeric(stock_cat[col], errors='coerce'))
            
        # convert to appropriate values by multiplying needed cols by 1000
        dollar_cols = ['Cash Flow', 'CapEx', 'Free Cash Flow', 'Cash On Hand', 'Long Term Debt']
        for col in dollar_cols:
            stock_cat[col] = stock_cat[col] * yahoo_adjust
        
        #Calculate net present value of the equity            
        stock_cat['DCF Value'] = npv.npv_fcf(stock_cat['Free Cash Flow'], 
                                         discount_rate, 
                                         years, 
                                         stock_cat['Conservative Analyst 5y'],
                                         multiplier,
                                         growth_decline,
                                         stock_cat['Cash On Hand'],
                                         stock_cat['Long Term Debt']
                                         )
        
        #Compares the Discounted Cash Flow to share price so decisions can be made about #what's overvalued and undervalued. Higher than 1 means undervalued
        stock_cat['DCF Share Price'] = stock_cat['DCF Value'] / stock_cat['Approx Shares Outstanding']
        stock_cat['DCF/Price Multiple'] = stock_cat['DCF Share Price']/stock_cat['Previous Close']
        
        #Give the period of reports using cash on hand report as proxy for data not reported
        stock_cat['Reporting Period'] = np.where(balance_data[0].iloc[2,1] == '-',
                                                 balance_data[0].iloc[0,2],
                                                 balance_data[0].iloc[0,1])
        stock_cat['Reporting Period'] = pd.to_datetime(stock_cat['Reporting Period'])
        
        #Preps needed categories for display
        stock_cat['Date'] = pd.to_datetime(datetime.date.today())
        stock_cat['Ticker'] = ticker.upper()
        stock_cat['Name'] = stocks[ticker][0]
        stock_cat['Categories'] = [stocks[ticker][1:]]

        #reorder the columns for more meaningful view
        stock_cat = stock_cat[list(stock_cat.columns[-4:]) + list(stock_cat.columns)[:-4]]
        
        #finally, add the entry to the list
        quotes.append(stock_cat.iloc[0])
    
    stock_frame = pd.DataFrame(quotes) #Turn these values into a dataframe
    stock_frame.replace('N/A (N/A)', np.nan, inplace=True) #properly indicate null values"
    stock_frame.set_index('Date', drop=True, inplace=True) #and prepare datetime indexing for better analysis
    
    return stock_frame #return a dataframe reflecting each entry

