import shutil
import os
import sys
import pytest
import tempfile
import shutil

# このファイルの親ディレクトリをシステムパスに追加する
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.utils.helper_funcs.check_disk import check_disk_space


@pytest.mark.parametrize("unit, ok_size_delta, attention_size_delta, write_size, expected_status", [
    ("MB", -7, -5, 6, "WARN"),       # WARN status test case
    ("MB", -10, -7, 6, "OK"),          # OK status test case
    ("MB", -5, -3, 6, "NG"),        # NG status test case
    ("KB", -800, -500, 300, "OK"),       # OK status test case (KB)
    ("GB", -0.3, -0.2, 0.1, "OK"),       # OK status test case (GB)
])
def test_check_disk_space(unit, ok_size_delta, attention_size_delta, write_size, expected_status):
    with tempfile.TemporaryDirectory() as temp_dir:
        # 空き容量が極端に不十分な一時ディレクトリを作成し、そのディスク容量をチェックする
        conv_factor = {"GB": 2 ** 30,"MB": 2 ** 20,"KB": 2 ** 10}.get(unit)
        temp_file = os.path.join(temp_dir, "temp.txt")
        free_size = shutil.disk_usage(temp_dir).free / conv_factor
        with open(temp_file, "wb") as f:
            f.write(os.urandom(int(write_size*conv_factor)))  # サイズwrite_size(unit)のランダムファイルを作成
        ok_size = free_size + ok_size_delta
        attention_size = free_size + attention_size_delta
        status = check_disk_space(temp_dir, attention_size, ok_size, unit)

        # ステータスが "NG" であることを検証する
        assert status == expected_status

