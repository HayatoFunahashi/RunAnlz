"""
=========================================================
Project : Nike Run Anlyze
File    : main.py
Description : example how to use

Copyright (c) 2022 Hayato Funahashi All Rights Reserved.
=========================================================
"""
import nike_anlyzer as na
import matplotlib.pyplot as plt
import seaborn as sns

def use_summary():
    anlyzer = na.NikeAnlyzer(b_need_fetch=False) #初回はTrueにする
    df = anlyzer.summary(b_first=True)
    print(df.info())
    df = df.drop(["nikefuel", "ascent", "descent", "steps", "speed"], axis=1)
    sns.pairplot(df)
    plt.show()

def use_timeseries():
    nike = na.NikeAnlyzer(b_need_fetch=False) #初回はTrueにする
    dfs = nike.time_series("pace", b_first=True) #ここでは例のため"ペース"データを得る
    df = dfs.iloc[0]
    print(df["data"].info())

use_summary()
use_timeseries()
print("all process complete.")