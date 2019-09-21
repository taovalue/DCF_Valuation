# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
stock_info = pd.read_html('https://finance.yahoo.com/quote/VEEV/key-statistics?p=VEEV')

stock_info[0]
stock_info[1]