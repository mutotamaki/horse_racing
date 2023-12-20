from bs4 import BeautifulSoup
import requests
from datetime import datetime
import numpy as np
import csv

def class_mapping(row):
    mappings = {'障害':0, 'G1': 10, 'G2': 9, 'G3': 8, '(L)': 7, 'オープン': 7, '3勝': 6, '1600': 6, '2勝': 5, '1000': 5, '1勝': 4, '500': 4, '新馬': 3, '未勝利': 1}
    for key, value in mappings.items():
        if key in row:
            return value
    return 0  # If no mapping is found, return 0

url_list = [
    "https://db.netkeiba.com/horse/2017105477",
    "https://db.netkeiba.com/horse/2017101431",
    "https://db.netkeiba.com/horse/2019105346",
    "https://db.netkeiba.com/horse/2018105165",
    "https://db.netkeiba.com/horse/2019104740",
    "https://db.netkeiba.com/horse/2018105269",
    "https://db.netkeiba.com/horse/2020102899",
    "https://db.netkeiba.com/horse/2018103559",
    "https://db.netkeiba.com/horse/2020103532",
    "https://db.netkeiba.com/horse/2017105379",
    "https://db.netkeiba.com/horse/2017102170",
    "https://db.netkeiba.com/horse/2019105283",
    "https://db.netkeiba.com/horse/2020103626",
    "https://db.netkeiba.com/horse/2020103458",
    "https://db.netkeiba.com/horse/2017104936",
    "https://db.netkeiba.com/horse/2019100109",
    "https://db.netkeiba.com/horse/2019105748",
    "https://db.netkeiba.com/horse/2017104691",
    "https://db.netkeiba.com/horse/2019102879",
    "https://db.netkeiba.com/horse/2019103588"
]  # スクレイピングしたいURLを指定

all_results = []  # 全てレース結果を保存するためのリスト

# cutoff_date = datetime.strptime('2023/05/27', '%Y/%m/%d')  # 特定の日付を指定
# 現在の日付を取得
now = datetime.now()
# cutoff_date を datetime 型に変換
cutoff_date = datetime.strptime(now.strftime('%Y/%m/%d'), '%Y/%m/%d')
for url in url_list:
    results = []  # 馬単位のレース結果を保存するためのリスト
    response = requests.get(url)

    # ステータスコードが200以外の場合はエラーが発生したとみなし、処理をスキップ
    if response.status_code != 200:
        print(f"Error occurred while fetching data from {url}")
        continue

    soup = BeautifulSoup(response.content, "html.parser")

    # テーブルを指定
    table = soup.find("table", {"class": "db_h_race_results nk_tb_common"})

    # テーブル内の全ての行を取得
    rows = table.find_all("tr")

    # 各行から必要な情報を取り出し
    for i, row in enumerate(rows[1:], start=1):# ヘッダ行をスキップ
        cols = row.find_all("td")

        # 日付を解析
        str_date = cols[0].text.strip()
        date = datetime.strptime(str_date, '%Y/%m/%d')

        # 特定の日付より前のデータのみを取得
        if date < cutoff_date:
            # 取得したいデータの位置を指定し取得
            #体重
            horse_weight = cols[23].text.strip()
            weight = 0
            weight_dif = 0
            try:
                weight = int(horse_weight.split("(")[0])
                weight_dif = int(horse_weight.split("(")[1][0:-1])
            except:
                weight = ''
                weight_dif = ''
            weight = weight
            weight_dif = weight_dif
            #上がり
            up = cols[22].text.strip()
            #通過順
            through = cols[20].text.strip()
            try:
                numbers = list(map(int, through.split('-')))
                through = sum(numbers) / len(numbers)
            except ValueError:
                through = ''
            #着順
            order_of_finish = cols[11].text.strip()
            try:
                order_of_finish = str(int(order_of_finish))
            except ValueError:
                order_of_finish = ""
            #馬番
            past_umaban = cols[8].text.strip()
            #騎手
            past_kishu = cols[12].text.strip()
            #斤量
            past_kinryo = cols[13].text.strip()
            #距離
            distance = cols[14].text.strip()
            #芝・ダート
            track = distance[0]
            shiba_mapping = {'芝': 0, 'ダ': 1, '障': 2}
            track = shiba_mapping.get(track)
            #距離
            distance = distance[1:]
            #レース名
            race_name = cols[4].text.strip()
            race_rank = class_mapping(race_name)
            #タイム
            time = cols[17].text.strip()
            try:
                time = float(time.split(':')[0]) * 60 + sum(float(x) / 10**i for i, x in enumerate(time.split(':')[1].split('.')))
            except:
                time = ''
            #天気
            weather = cols[2].text.strip()
            tenki_mapping = {'晴': 0, '曇': 1, '小': 2, '雨': 3, '雪': 4}
            weather = tenki_mapping.get(weather)
            #オッズ
            odds = cols[9].text.strip()
            track_condition = cols[15].text.strip()
            #馬場状態
            baba_mapping = {'良': 0, '稍': 1, '重': 2, '不': 3}
            track_condition = baba_mapping.get(track_condition)
            
            result = [str_date,past_umaban,past_kishu,past_kinryo, odds, weight, weight_dif, up, through, order_of_finish, distance, race_rank, time, track, weather, track_condition,"",""]
            results.append(result)

            # 5行取得したら終了
            if len(results) >= 5:
                # 最終アウトプットに追加
                # 横に連結
                # resultsをnumpy配列に変換
                results_array = np.array(results)

                # numpy配列を1次元に変換
                flattened_results = results_array.ravel()
                all_results.append(flattened_results)
                break

            # 最終ループを判定
            if i == len(rows[1:]):
                if results:  # resultsが空でない場合
                    results_array = np.array(results)
                    flattened_results = results_array.ravel()
                    all_results.append(flattened_results)

# データをCSVファイルに出力する
with open('race_data/t_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    for data in all_results:
        writer.writerow(data)