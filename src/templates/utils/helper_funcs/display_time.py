# Displays time information in a specified format
import datetime
import time

def timestamp2str(now, format="jap"):
    """
    現在の日付と時刻を取得するための関数
    :Parameters:
        :now: float型。time.time()の戻り値かdatetime.datetimeオブジェクト
        :format: 文字列。出力フォーマットを指定する ("jap", "iso", "us", "uk")
    :Returns:
        :now_ymdhms: 現在の年月日時分秒
    """

    if isinstance(now, float):
        now_dt = datetime.datetime.fromtimestamp(now)
    elif isinstance(now, datetime.datetime):
        now_dt = now
    else:
        raise ValueError("""無効な入力です。'now'はdatetime.datetimeオブジェクトかtime.time()の出力でなければなりません。""")

    if format == "jap":
        now_ymdhms = now_dt.strftime("%Y年%m月%d日%H時%M分%S秒")
    elif format == "iso":
        now_ymdhms = now_dt.isoformat()
    elif format == "us":
        now_ymdhms = now_dt.strftime("%m/%d/%Y %I:%M:%S %p")
    elif format == "uk":
        now_ymdhms = now_dt.strftime("%d/%m/%Y %H:%M:%S")
    else:
        raise ValueError("無効なフォーマットです。対応しているフォーマット: 'jap', 'iso', 'us', 'uk'。")

    return now_ymdhms



if __name__ == "__main__":
    now = time.time()
    formatted_time = timestamp2str(now, format="iso")
    print(formatted_time)

    now = datetime.datetime.now()
    formatted_time = timestamp2str(now, format="jap")
    print(formatted_time)

    try:
        formatted_time = timestamp2str("invalid_input")
    except ValueError as e:
        print(e)

    
    try:
        now = time.time()
        formatted_time = timestamp2str(now, format="unsupported_format")
    except ValueError as e:
        print(e)