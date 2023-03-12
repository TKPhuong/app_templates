import time
import datetime
import sys
import os

# このファイルの親ディレクトリをシステムパスに追加する
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.utils.helper_funcs.display_time import timestamp2str


def test_timestamp2str():
    # エポックタイムから現在時刻を取得する
    now = time.time()

    # time2datetime関数で現在時刻を変換する
    now_ymdhms = timestamp2str(now)

    # 現在時刻をdatetimeオブジェクトに変換する
    now_datetime = datetime.datetime.fromtimestamp(now)

    # 現在時刻を年月日時分秒の形式に変換する
    now_formatted = now_datetime.strftime("%Y年%m月%d日%H時%M分%S秒")

    # time2datetime関数が期待通りの結果を返すことを確認する
    assert now_ymdhms == now_formatted
