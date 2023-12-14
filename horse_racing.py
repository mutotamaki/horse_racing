import pandas as pd
from bs4 import BeautifulSoup
import time
import requests
import re

calendar_url = "https://race.netkeiba.com/top/calendar.html?year=2023&month={}"

start_month = 1
end_month = 12

# 日付部分を格納するリストを作成
race_id_list = []

# 1月1日から12月31日までの各日に対応するURLを生成し、該当するaタグを取得します
for month in range(start_month, end_month + 1):
    # 日付に対応するURLを生成します
    url = calendar_url.format(month)
    
    # 対象サイトにアクセスする前に少し待機します
    time.sleep(1)
    
    # Webサーバにリクエストを出します
    r = requests.get(url)
    
    # HTMLソースをBeautifulSoupオブジェクトに変換します
    html_soup = BeautifulSoup(r.text, 'html.parser')
    
    # aタグを持ってきます
    a_tags = html_soup.find_all('a', href=True)

    # href属性が条件を満たすものを取得します
    for a_tag in a_tags:
        href = a_tag.get('href')
        if href and "../top/race_list.html?kaisai_date=2023" in href:
            # 正規表現を使って日付部分を抽出し、リストに追加
            # match(/正規表現/修飾子, "対象文字列")
            # \d -> 0～9の数値。[0-9] と同じ。
            # A+ -> 1文字以上のAが続く
            # \d+ -> 1文字以上の0～9の数値が続く
            date_match = re.search(r'kaisai_date=(\d+)', href)
            if date_match:  # 正規表現の検索が成功した場合（日付部分が見つかった場合）

              # .groupメソッドは、引数を0or省略の場合、パターンにマッチした文字列全体を返す
              # 1 以上の値(最大99)を指定した場合は、対応するキャプチャグループによってマッチした部分文字列を返す
              date_part = date_match.group(1)
              # 日付部分をリストに追加する
              race_id_list.append(date_part)

race_result_page = "https://race.netkeiba.com/top/race_list.html?kaisai_date={}"

# race_id_list内の日付部分を使用してURLを生成し、race_result_pageに格納する
race_result_page_list = [race_result_page.format(date) for date in race_id_list]

# race_result_page_list内のURLを表示する
for url in race_result_page_list:
    print(url)