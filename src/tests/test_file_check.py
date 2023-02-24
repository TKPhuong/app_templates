import os
import pytest
import tempfile
import sys

# このファイルの親ディレクトリをシステムパスに追加する
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.utils.helper_funcs.file_check import check_file

def test_check_file_success():
    # テンポラリディレクトリに作成した一時ファイルがディレクトリに存在する場合はTrueを返すことを確認する。
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, "temp_file.txt")
        with open(temp_file_path, "w") as f:
            f.write("test data")
        assert check_file("temp_file.txt", temp_dir, 404) == True

def test_check_file_failure():
    # ファイルがディレクトリに存在しない場合は、FileNotFoundErrorを発生させることを確認する。
    with pytest.raises(FileNotFoundError) as exc_info:
        check_file("nonexistent_file.txt", ".", 404)
    assert exc_info.type is FileNotFoundError
    assert exc_info.value.args[0] == "ファイル 'nonexistent_file.txt' がディレクトリ '.' に見つかりませんでした。エラーコード: 404"
