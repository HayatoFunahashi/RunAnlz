"""
=========================================================
Project : Nike Run Anlyze
File    : nike_collector.py

Copyright (c) 2022 Hayato Funahashi All Rights Reserved.
=========================================================
"""
import requests
import json
import datetime

class NikeDataCollecter():
    """Nikeのログデータ収集用クラス"""
    __init_act_url = "https://api.nike.com/sport/v3/me/activities/after_time/0"
    __next_act_url = "https://api.nike.com/sport/v3/me/activities/after_id/"
    __uniq_act_url = "https://api.nike.com/sport/v3/me/activity/"
    __id_cache_path = "work/act_ids"
    __save_dir = "log"
    __token_path = "work/token"

    def __fetch_nike_api(self, url, params=None):
        """ nike.comからfetchする共通api """
        with open(self.__token_path) as f:
            bearer_token = f.read().strip()

        headers = {'Authorization': 'Bearer {}'.format(bearer_token)}
        r_get = requests.get(url=url, headers=headers, params=params)
        r_get = r_get.json()
        if(r_get.get("error_id") is None):
            return r_get
        else:
            return False

    def __fetch_save(self, id):
        """fetchのメイン関数 

        Notes:
        --------
        走行データをfetchして__save_dirに.jsonとして保存する
        保存条件:heart_rateが含まれること
        
        Returns:
        --------
        bool : 
            True:Saveした
            False:Saveしなかった
        """
        params = {'metrics':'all'}
        url= self.__uniq_act_url + id
        data = self.__fetch_nike_api(url, params=params)
        if data is not False:
            # 保存する条件を決める
            need_save = "heart_rate" in data.get("metric_types")
            if(need_save):
                epoch = data.get("start_epoch_ms")
                epoch_utc = datetime.datetime.fromtimestamp(epoch/1000) # utc時刻へ変換
                with open('{}/act_{}.json'.format(self.__save_dir, epoch_utc), 'w') as f:
                    json.dump(data, f, indent=4)
                return True
        return False

    def __extract_all_actid(self):
        """Nike Apiに問い合わせして全てのActivity idリストを取得する"""
        url = self.__init_act_url
        data = self.__fetch_nike_api(url)
        if data is False:
            return None
        act_ids = [d.get("id") for d in data["activities"]]

        # idリストが1ページに収まらない場合は次ページが存在
        # after_idを使って次ページからもidを取得
        after_id = data["paging"].get("after_id")
        while(after_id is not None):
            url = self.__next_act_url+ after_id
            data = self.__fetch_nike_api(url)
            ids = [d.get("id") for d in data["activities"]]
            act_ids.extend(ids)
            after_id = data["paging"].get("after_id")
        return act_ids

    def __fetch_main(self):
        #キャッシュ済みデータの読み出し
        with open(self.__id_cache_path, 'r') as f:
            cached_ids = [d.replace('\n', '') for d in f.readlines()]    #改行コードを変換
            if cached_ids is None:
                cached_ids = []

        #全てのactivity_idを問い合わせて取得
        all_ids = self.__extract_all_actid()
        if all_ids is None:
            print("all_ids fetch fail")
            return False

        #未キャッシュ≒fetchが必要
        non_cache_ids = list(set(all_ids) - set(cached_ids))
        if non_cache_ids == []:
            print("No need fetch")
            return False

        #読み出し＆キャッシュ開始
        for id in non_cache_ids:
            ret = self.__fetch_save(id)
            print("{}:{}".format("saved" if ret else "unsaved", id))
        
        #処理したidリストを保存
        f = open(self.__id_cache_path, 'w')
        f.write('\n'.join(all_ids))
        f.close()
        return True
    
    def get_save_dir(self):
        """保存したディレクトリパスのgetter"""
        return self.__save_dir

    def fetch(self):
        """fetchの公開呼び出し関数
        
        Note:
        -------
        Nike.comからデータ取得とキャッシングを実行.fetch失敗時もそのまま抜ける.
        
        fetchが失敗する例:
        -------
            ・BearerTokenの有効期限切れ  
            ・Nike.comにアクセスできない
        """
        if self.__fetch_main():
            print("fetch done.")
        else:
            print("fetch process abort")