import shutil

def check_disk_space(folder: str, attention_size: float, ok_size: float, unit: str = "GB") -> str:
    """
    指定されたフォルダーのディスクスペースをチェックして、空き容量に応じたステータスを返します。

    :param folder: ディスクスペースをチェックするフォルダーのパス。
    :param attention_size: 警告を発生させるしきい値。この値よりも大きい場合、ステータスは OK となります。
    :param ok_size: クリティカルなアラートを発生させるしきい値。この値よりも大きい場合、ステータスは WARN となります。
    :param unit: 空き容量チェックに使用する単位。これは "GB"（ギガバイト）、"MB"（メガバイト）、または "KB"（キロバイト）のいずれかで指定できます。デフォルトは "GB" です。

    :return: ディスクスペースの空き容量に基づくステータスを示す文字列。OK、WARN、NG のいずれか。
    """
    # ユニット名と変換係数を対応付ける辞書を定義
    conversion_factors = {
        "GB": 2 ** 30,
        "MB": 2 ** 20,
        "KB": 2 ** 10,
    }

    # 指定されたユニット名に対応する変換係数を取得し、存在しない場合は "GB" を使用する
    conversion_factor = conversion_factors.get(unit, conversion_factors["GB"])

    # ディスクスペースを指定された単位に変換する
    total, used, free = shutil.disk_usage(folder)
    free_disk = free / conversion_factor

    # ステータスをチェックする
    if free_disk > attention_size:
        status = "OK"
    elif free_disk > ok_size:
        status = "WARN"
    else:
        status = "NG"

    return status
