import os
import sys

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir =  os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from templates.system.constant import ConstantMaker

class States(metaclass=ConstantMaker):
    """
    システムの状態を表す定数を定義するクラスです。
    """
    STARTUP = "スタートアップ"
    INITIATING = "処理化中"
    INITIATED = "処理化済み"
    IDLE = "タスク待ち"
    PROCESSING = "タスク処理中"
    ERROR = "エラー発生中"
    CLEANUP = "クリーンアップ"
    EXITED = "終了"

APP_INIT_STATS = {"STATE":States.STARTUP}
THREAD_INIT_STATS = {"STATE":States["start_up"]}