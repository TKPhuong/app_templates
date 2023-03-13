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
    start_up = "STARTUP"
    initiating = "INITIATING"
    initiated = "INITIATED"
    idle = "IDLE"
    process = "PROCESSING"
    error = "ERROR"
    cleanup = "CLEANUP"

APP_INIT_STATS = {"STATE":States.start_up}
THREAD_INIT_STATS = {"STATE":States["start_up"]}