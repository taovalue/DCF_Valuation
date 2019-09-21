# -*- coding: utf-8 -*-
"""
Function for DCF (Discounted Cash Flow)

designed by Nick Kraackman, founder of Value Spreadsheet

Created on Fri Sep 20 10:34:33 2019

@author: patrick.fang
"""

def npv_fcf(fcf, discount_rate, years, growth_rate, multiplier, growth_decline_rate, cash_on_hand, total_debt):
    '''Calculates net present value of a free cash flow over a given time period'''
    
    npv = [] #initialize a list
    
    #Add values depending on year, growth rate, growth decline, and discount ratefor year in range(1, years+1):
    fcf = fcf * (1 + growth_rate)/((1 + discount_rate))
    growth_rate = growth_rate * (1-growth_decline_rate)
    
    final_fcf = fcf

    npv.append(fcf)
    
    max_year_fcf_value = final_fcf * multiplier #Year 10NPV Value
    npv.append(max_year_fcf_value) 
    
    npv.append(cash_on_hand)
    npv.append(-total_debt)
    
        
    return sum(npv)