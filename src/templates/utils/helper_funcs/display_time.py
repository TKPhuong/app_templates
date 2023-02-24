# Displays time information in a specified format
import datetime


def time2datetime(now):
    """
    現在の日付と時刻を取得するための関数
    :Parameters:
        :now: float型。time.time()の戻り値
    :Returns:
        :now_ymdhms: 現在の年月日時分秒
    """
    # 現在の年、月、日、時、分、秒
    now_ymdhms = datetime.datetime.fromtimestamp(now)
    now_ymdhms = now_ymdhms.strftime("%Y年%m月%d日%H時%M分%S秒")
    return now_ymdhms
