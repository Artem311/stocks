#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import pandas as pd
import streamlit as st
import altair as alt
from urllib.error import URLError
import numpy as np
import matplotlib.pyplot as plt
import tkinter
import matplotlib
import scipy
import warnings
import datetime
import requests
import apimoex
import bt

class WeighTarget(bt.Algo):
    def __init__(self, target_weights):
        self.tw = target_weights

    def __call__(self, target):
        if target.now in self.tw.index:
            w = self.tw.loc[target.now]
            target.temp['weights'] = w.dropna()
        return True

def get_hurst_exponent(time_series):
    """Returns the Hurst Exponent of the time series"""
    time_series=time_series.tolist()
    max_lag=50
    lags = range(2, max_lag)
    # variances of the lagged differences
    tau = [np.std(np.subtract(time_series[lag:], time_series[:-lag])) for lag in lags]
    # calculate the slope of the log plot -> the Hurst Exponent
    reg = np.polyfit(np.log(lags), np.log(tau), 1)
    return reg[0]

@st.cache
def get_data_w_today(name, start, end):
    with requests.Session() as session:
        if name =='IMOEX':
            data = apimoex.get_board_history(session, name, start, end, market='index', board='SNDX')
        elif name in ['RTSI','MCFTR']:
            data = apimoex.get_board_history(session, name, start, end, market='index', board='RTSI')
        else:
            data = apimoex.get_board_history(session, name, start, end)
        df = pd.DataFrame(data)
        df=df.rename(columns={'CLOSE':name,'TRADEDATE':'Date'})[[name,'Date']]
        df['Date']=pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        df=df.fillna(method='pad')
        request_url = ('https://iss.moex.com/iss/engines/stock/'
               'markets/shares/boards/TQBR/securities.json')
        arguments = {'marketdata.columns': ('SECID,'
                                            'BOARDID,'
                                           'LAST,'
                                           'OPEN')}
        with requests.Session() as session:
            iss = apimoex.ISSClient(session, request_url, arguments)
            data_1 = iss.get()
            df_1 = pd.DataFrame(data_1['marketdata'])
            df_1.set_index('SECID', inplace=True)
        df.loc[end]=df_1.loc[name]['LAST']
        df.index=pd.to_datetime(df.index)
    return df


def main():
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Exploration"])
    list_of_ass=['LKOH','GMKN','NVTK','POLY','MGNT','MTSS','ALRS','NLMK',
    'MOEX','CHMF','SNGSP','SBERP','SBER','TATNP','TATN','PHOR','MAGN','YNDX','SIBN','PLZL','GAZP','ROSN','TCSG']
    if page == "Homepage":
        delta=3*365
        start=(datetime.datetime.now()-datetime.timedelta(days=delta)).strftime('%Y-%m-%d')
        now=datetime.datetime.now().strftime('%Y-%m-%d')
        st.title("Data Exploration")
        name = st.selectbox("Choose a stock", list_of_ass, index=3)
        data = get_data_w_today(name, start, now)
        fig, ax= plt.subplots(figsize=(15,10))
        ax.plot(data)
        ax.set_title(name+' historic price')
        st.pyplot(fig)
    elif page == "Exploration":
        st.selectbox("Choose a stock", list_of_ass, index=4)


if __name__ == '__main__':
    main()
    
    
    

