# Nike Running App Anlyzer

## 概要
APIをNikeRunClubの走行データを取得します．また，解析用に前処理します．

## マニュアル
主な使用方法はmain.pyを参考にしてください  
前処理で得られるデータ種別はsummaryとtime-seriesデータです．いずれも型はDataframeです．
* summary : ランごとの総走行距離や平均速度や平均心拍数など，サマリーデータ群です  
* time-series : ラン中の時系列データ群を返します．取得するデータはanalyzerのmetricsに指定してください．

ライブラリは以下の３つで構成されます
1. nike_anlyzer.py : 走行データの前処理+解析用ラッパーライブラリ．解析したい内容に応じてsummary, time-seriesを指定してください．ユーザアプリからは本クラスをコールしてください．
2. nike_collector.py : Nikeの走行データfetch用ライブラリ
3. nike_postProcessor.py : 走行データをsummaryデータと時系列データのDataframeに前処理するライブラリ


## 補足

* データをNike.comから取得する場合はwork/tokenにBearer Tokenの値を書き込む.tokenは`一定時間(30minくらい)で変更される`ので注意
 > tokenの詳細については[Qiita記事](https://qiita.com/h_funa/items/a9950dccd6bb4d4cf750)や[先人の投稿](https://gist.github.com/niw/858c1ecaef89858893681e46db63db66)を参照
* データ取得は一度目以降は`b_need_fetch=True`としてローカルデータを利用することを推奨します
