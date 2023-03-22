import os


def check_file(f_name, dir_name, error_code=1):
    """指定されたディレクトリに指定されたファイルが存在するかどうかをチェックする。

    Args:
        f_name (str): チェックするファイル名。
        dir_name (str): ファイルを検索するディレクトリ名。
        error_code (int): ファイルが存在しなかった場合に発生させるエラーコード。

    Returns:
        bool: ファイルがディレクトリに存在する場合はTrue、それ以外はFalseを返す。
    """
    file_path = os.path.join(dir_name, f_name)

    if os.path.isfile(file_path):
        return True
    else:
        error_message = (
            f"ファイル '{f_name}' がディレクトリ '{dir_name}' に見つかりませんでした。エラーコード: {error_code}"
        )
        raise FileNotFoundError(error_message, error_code)

if __name__ == "__main__":
    pass

import tempfile
import os

with tempfile.TemporaryDirectory() as directory_name:
    # 存在するファイルの例
    file_name = "test.txt"

    # 存在しないファイルの例
    nonexist_file_name = "nonexistent.txt"
    error_code = 1

    # テスト用のファイルを作成
    with open(os.path.join(directory_name, file_name), "w") as f:
        f.write("test")

    try:
        check_file(file_name, directory_name, error_code)
        print("ファイルが存在します。")
        check_file(nonexist_file_name, directory_name, error_code)
    except FileNotFoundError as e:
        print(e)
