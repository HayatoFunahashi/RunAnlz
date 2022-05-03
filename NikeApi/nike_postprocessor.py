"""
=========================================================
Project : Nike Run Anlyze
File    : nike_postprocessor.py

Copyright (c) 2022 Hayato Funahashi All Rights Reserved.
=========================================================
"""
import json
import datetime
import pandas as pd

class NikePostProcessor():
    __summary_path = "work/summary.pkl"
    __timesrs_path = "work/time_series.pkl"

    def __init__(self, paths) -> None:
        self.paths = paths
        pass

    def __mk_summary_single_df(self, jd):
        """引数で渡したjsonファイルをsummaryのDataFrameに変換する"""
        s_time = jd.get("start_epoch_ms")
        s_time = datetime.datetime.fromtimestamp(s_time/1000) #msデータなので1000で除してUTC時間に変換
        d_time = jd.get("active_duration_ms")
        d_time = d_time/1000/60 #ms -> min変換
        
        ret = {}
        ret["start_utc_ms"] = pd.Series(s_time)
        ret["active_duration_min"] = pd.Series(d_time)
        for d in jd.get("summaries"):
            key = d.get("metric")
            val = d.get("value")
            ret[key] = pd.Series(val)
        
        return pd.DataFrame(ret)

    def __mk_single_ts_df(self, jd, metric):
        """引数で渡したjsonファイルからmetricで指定したパラメタの時系列DataFrameに変換"""        
        for d in jd.get("metrics"):
            if d.get("type") == metric:
                df = pd.json_normalize(d.get("values"))
                break
        if df is None:
            return None
                
        # unix時間に変換
        for index in df.columns:
            if('epoch_ms' in index):
                df[index] = df.apply(lambda x: datetime.datetime.fromtimestamp(x[index]/1000), axis=1)
        
        # column名をepoch->utcに変更
        df = df.rename(columns={"start_epoch_ms":"start_utc_ms", "end_epoch_ms":"end_utc_ms"})

        #開始時刻からの経過時間(delta time)を算出
        start_time = df.iloc[0]["start_utc_ms"]
        dt = pd.Series((df["start_utc_ms"] - start_time), name='dt_utc_ms')
        df = pd.concat([df, dt], axis=1)
        return df

    def create_save_summary_df(self):
        """サマリーデータの作成

        Notes:
        作成したサマリーデータは__summary_pathに.pklでキャッシュする
        キャッシュした.pklはread_summary_df()で取得可能
        """
        new = None; old = None
        for path in self.paths:
            jd = json.load(open(path, 'r'))
            old = self.__mk_summary_single_df(jd)
            if new is None:
                new = old
            else:
                new = pd.concat([new, old])
        ret = new.sort_values("start_utc_ms", ascending=False, ignore_index=True)
        ret.to_pickle(self.__summary_path)
        return ret
    
    def read_summary_df(self):
        return pd.read_pickle(self.__summary_path)
        
    def create_save_timeseries_dfs(self, type):
        """時系列(Time-Series)データの作成

        Notes:
        作成したデータは__timesrs_pathに.pklでキャッシュする
        キャッシュした.pklはread_timeseries_dfs()で取得可能
        """
        ret_dfs = None
        for path in self.paths:
            jd = json.load(open(path, 'r'))
            s_time = datetime.datetime.fromtimestamp(jd.get("start_epoch_ms")/1000) #unix->utc変換

            df = self.__mk_single_ts_df(jd, type)
            new_df = pd.DataFrame(data=[[s_time, df]], columns=["start_utc", "data"])
            
            if ret_dfs is None:
                ret_dfs = new_df
            else:
                ret_dfs = pd.concat([ret_dfs, new_df])
        ret_dfs.to_pickle(self.__timesrs_path)
        return ret_dfs
    
    def read_timeseries_dfs(self):
        return pd.read_pickle(self.__timesrs_path)