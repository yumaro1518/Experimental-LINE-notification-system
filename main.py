import sys
import csv
import urllib.request, urllib.error
from bs4 import BeautifulSoup
from notify import LINENotifyBot
import logging

# STEP1:ログの記録するフォーマットを決める

#(levelname)sはログレベル（INFO、DEBUG、ERRORなど）・(asctime)sはログが出力された時刻・%(message)sはログメッセージ
log_format = '%(levelname)s : %(asctime)s : %(message)s'
#basicConfig()関数を使用して、ログの基本設定→引数に情報を引き渡す
#filename='event.log': ログを出力するファイルの名前を指定・level=logging.INFO: ログレベルを設定・format=log_format: 先ほど定義したログのフォーマットを指定
logging.basicConfig(filename='event.log', level=logging.INFO, format=log_format)
#info()関数を使用してログを出力→メッセージは'START'という文字列。このログは設定に従って、指定されたファイル(今回は'event.log')に記録される。
logging.info('START')
url = "https://it-chiba.com/nyushi/enrollment/"
bot = LINENotifyBot('orr6QtfB1wfx00m1PFrXcDFNASJSlhabw7OLULuFdvP')

#　STEP2:指定されたURLからHTMLを取得し、その取得の成否をログに記録すると同時に、LINE Notifyを使用して通知する工程

#Pythonでは、エラーが発生する可能性のあるコードをtryブロックで囲み、その後にexceptブロックを配置してエラー処理を行う
try:
    # HTMLを取得する
    html = urllib.request.urlopen(url)
    # HTMLのステータスコード（正常に取得できたかどうか）を記録する
    logging.info('HTTP STATUS CODE: ' + str(html.getcode()))
except:
    # 取得に失敗した場合もLINEに通知してログを取る
    bot.send('URLの取得に失敗しました')
    # 念の為強制終了　sys.exit()関数はプログラムを強制終了→引数の1はプログラムの異常終了を示す終了コード
    sys.exit(1)

#　STEP3：BeautifulSoupを使用してHTMLから全てのリングを抽出し、前回習得したリンクと比較して新しいリンクを特定する工程

soup = BeautifulSoup(html, "html.parser")
# HTMLの中から全てのaタグを抽出
tags = soup.find_all("a")
links = list()
# 前回取ったリンク
oldlinks = set()
# 今回とったリンク
newlinks = set()
for tag in tags:
    # aタグからリンクのURLのみを取り出す。
    links.append(tag.get('href'))
try:
    # 前回取得したリンクをファイルから読み込む
    with open('event.log', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            oldlinks = set(row)
        logging.info('Opened csv file"')
except:
    # 何かしら失敗した場合はLINEに通知、ログ
    bot.send('ファイルの取得に失敗しました')
    logging.error('Failed to get csv file')

try:
    # 今回取得したリンクを記録する（上書き）
    with open('event.log', 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(links)
    logging.info('Writed csv file')
except:
    # 失敗したら通知、ログ
    bot.send('ファイルの書き込みに失敗しました')
    logging.error('Failed to write csv file')
    sys.exit(1)

# STEP4:

try:
    newlinks = set(links)
    # setで引き算をすると差分がわかる
    # 今回新しく発見したリンク
    added = newlinks - oldlinks
    # 前回あったけど今回はなくなったリンク
    removed = oldlinks - newlinks
    for link in added:
        # 追加されたら通知
        # 追加されたURL自体もお知らせしようとしたらリンクをむやみに貼るなと書いてあったので一応やめておいた
        bot.send('リンクが追加されました')

    for link in removed:
        # 追加と同様に
        bot.send('リンクが消去されました')

    logging.info('Compared links')

except:
    # 失敗したら…（以下略）
    bot.send('比較に失敗しました')
    logging.error('Failed to compare')
    sys.exit(1)

logging.info('DONE')
