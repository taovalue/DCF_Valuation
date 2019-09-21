# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 10:39:32 2019

@author: patrick.fang
"""
# import modules
import pandas as pd #data processing
import pygsheets #export to Google Sheets
import numpy as np #numerical processing
import datetime #enable datetime manipulation
pd.set_option('max_columns', 500) #more columns makes it easier to work with wide datasets

# import custom modules (make sure the .py files are in the same working directory of this script)
import trackr as tk


#Dictionary of stocks requested to track. Key is ticker symbol, list position 1 is name, and subsequent positions are categories to which the company belongs.

'''
br_stocks = {'aapl': ['Apple', 'Cell Phone'], 
             '005930.KS': ['Samsung', 'Cell Phone'],
             't': ['ATT', 'Cell Service Provider', 'ISP'],
             'vz': ['Verizon', 'Cell Service Provider'],
             'cmcsa': ['Comcast', 'ISP'],
             'chtr': ['Charter', 'ISP'],
             'googl': ['Google', 'Search'],
             'fb': ['Facebook', 'Advertising'],
             'twtr': ['Twitter', 'Twitter'],
             'kr': ['Kroger', 'Kroger'],
             'msft': ['Microsoft', 'Cloud Storage'],
             'ibm': ['IBM', 'Cloud Storage'],
             'crm': ['Salesforce', 'Cloud Storage']}
'''

# dcf_trackr = trackr(br_stocks)

test = tk.trackr({'veev': ['Veeva', 'Software']})

quotes = test[['Ticker', 'Name', 'Categories', 'Previous Close', 'Market Cap', 'Cash Flow', 
                     'CapEx', 'Free Cash Flow', 'Cash On Hand', 'Long Term Debt', 'Approx Shares Outstanding', 
                     'Conservative Analyst 5y', 'DCF Value', 'DCF Share Price', 'DCF/Price Multiple', 'Reporting Period']]

#Publish to Google Sheets
'''
sheet_auth = ''
sheet_name = 'y_finance_stocks'
gc = pygsheets.authorize(service_file=sheet_auth)
sh = gc.open(sheet_name)
wks = sh[0]
wks.set_dataframe(quotes.reset_index(), (1,1)) #specifies cell coordinates of upper leftmost cell
'''

