import shutil


def check_disk_space(folder: str, attention_size: int, ok_size: int):
    """
    ディスクスペースの容量をチェックする。
    :Parameters:
        :folder: ディスクスペースをチェックするフォルダーのパス
        :attention_size: 警告を出すしきい値。この値よりも大きい場合、ステータスは OK となる。
        :ok_size: 正常な状態とするしきい値。この値よりも大きい場合、ステータスは WARN となる。
    :Returns:
        :status: ディスクスペースの容量に基づくステータスを返す。OK, WARN, NG のいずれか。
    """
    # ディスクの容量をGBに変換
    total, used, free = shutil.disk_usage(folder)
    free_disk = free / (2 ** 30)

    # ステータスをチェック
    if free_disk > attention_size:
        status = "OK"
    elif free_disk > ok_size:
        status = "WARN"
    else:
        status = "NG"

    return status

