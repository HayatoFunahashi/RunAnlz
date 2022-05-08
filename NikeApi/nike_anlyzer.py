"""
=========================================================
Project : Nike Run Anlyze
File    : nike_anlyzer.py

Copyright (c) 2022 Hayato Funahashi All Rights Reserved.
=========================================================
"""

import json
import glob
import csv
import nike_collector as nc
import nike_postprocessor as npp

class NikeAnlyzer:
    """
    Nikeデータの解析クラス
    
    Attributes
    ----------
    paths : list[str]
        ファイルパスのリスト
    valid_metrics : list[str]
        有効なmetric typeの種別リスト
    """

    def __init__(self, b_need_fetch) -> None:
        """
        Parameters
        ----------
        b_need_fetch : bool
            Nike.comからデータをfetchするかどうか
        """
        collecter = nc.NikeDataCollecter()
        if b_need_fetch:
            collecter.fetch()
        dir = collecter.get_save_dir()

        self.__paths = glob.glob("{}/*.json".format(dir))
        # 有効なメトリクス種別を取得
        jd = json.load(open(self.__paths[0], 'r'))
        self.__valid_metrics = jd.get("metric_types")
        csv.writer(open("work/metric", 'w')).writerow(self.__valid_metrics)
        pass

    def summary(self, b_first):
        """
        Summaryデータの解析処理本体

        Parameters
        ----------
        b_first : bool
            初めて解析する場合はtrueにする 以降はキャッシュされるのでFalseで良い
        
        Returns
        ----------
        df : DataFrame サマリーデータ
        """
        pp = npp.NikePostProcessor(self.__paths)
        if b_first:
            df = pp.create_save_summary_df()
        else:
            df = pp.read_summary_df()
        return df
    
    def time_series(self, metric_type, b_first):
        """
        時系列(time_series)データの解析処理本体

        Parameters
        ----------
        metric_type : str
            解析対象のmetricを指定 指定したmetricが含まれない場合は処理しない
        b_first : bool
            初めて解析する場合はtrueにする 以降はキャッシュされるのでFalseで良い
        
        Returns
        ---------
        dfs : DataFrame 時系列データ群
        """
        if metric_type in self.__valid_metrics:
            pp = npp.NikePostProcessor(self.__paths)
            if b_first:
                dfs = pp.create_save_timeseries_dfs(metric_type)
            else:
                dfs = pp.read_timeseries_dfs()
            return dfs
        elif metric_type == "all":
            pp = npp.NikePostProcessor(self.__paths)
            # 全データをローカルに保存する
            for metric in self.__valid_metrics:
                print(metric + " do ....")
                dfs = pp.create_save_timeseries_dfs(metric)
        else:
            print("invalid metric type given.")
            return None
