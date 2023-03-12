import copy

class StatusTracker:
    """
    システムの状態を追跡するためのクラス。

    Attributes
    ----------
    _instances : dict
        このクラスのインスタンスを管理するクラス変数。

    Methods
    -------
    __new__(cls, id, initial_status)
        新しい StatusTracker オブジェクトを作成する。

    update_status(status_name, value)
        ステータスを更新する。

    get_status(status_name)
        ステータスの値を取得する。

    reset()
        ステータスを初期値にリセットする。

    delete_instance(id)
        指定された ID の StatusTracker インスタンスの削除を行う。

    delete_all_instances()
        すべての StatusTracker インスタンスを削除する。

    get_instance(id)
        指定された ID の StatusTracker インスタンスを取得する。

    __getitem__(status_name)
        ステータスの値を取得する。

    __setitem__(status_name, value)
        ステータスの値を設定する。

    __repr__()
        StatusTrackerインスタンスの文字列表現を返す。

    __iter__()
        ステータスとその値について反復処理する。

    """

    _instances = {}

    def __new__(cls, id, initial_status):
        """
        新しい StatusTracker オブジェクトを作成する。

        Parameters
        ----------
        id : str
            システム ID。
        initial_status : dict
            初期状態のステータス辞書。

        Returns
        -------
        StatusTracker
            新しい StatusTracker オブジェクト。

        """
        if id not in cls._instances:
            cls._instances[id] = super().__new__(cls)
            cls._instances[id]._id = id
            cls._instances[id]._initial_status = copy.deepcopy(initial_status)
            cls._instances[id]._statuses = copy.deepcopy(initial_status)
        return cls._instances[id]

    def update_status(self, status_name, value):
        """
        ステータスを更新する。

        Parameters
        ----------
        status_name : str
            更新するステータスの名前。
        value : any
            新しいステータスの値。

        """
        self[status_name] = value

    def get_status(self, status_name):
        """
        ステータスの値を取得する。

        Parameters
        ----------
        status_name : str
            取得するステータスの名前。

        Returns
        -------
        any
            ステータスの値。

        """
        return self[status_name]

    def reset(self):
        """
        ステータスを初期値にリセットする。

        """
        self._statuses = copy.deepcopy(self._initial_status)
        for key in self._initial_status:
            setattr(self, key, self._initial_status[key])

    @classmethod
    def delete_instance(cls, id):
        """
        指定された ID の StatusTracker インスタンスの削除を行う。

        Parameters
        ----------
        id : str
            削除する StatusTracker インスタンスの ID。

        """
        del cls._instances[id]

    @classmethod
    def delete_all_instances(cls):
        """
        すべての StatusTracker インスタンスを削除する。

        """
        cls._instances = {}

    @classmethod
    def get_instance(cls, id):
        """
        指定された ID の StatusTracker インスタンスを取得する。

        Parameters
        ----------
        id : str
            取得する StatusTracker インスタンスの ID。

        Returns
        -------
        StatusTracker or None
            指定された ID の StatusTracker インスタンス。存在しない場合は None。

        """
        return cls._instances.get(id, None)

    def __iter__(self):
        """
        ステータスとその値について反復処理する。

        Returns
        -------
        StatusIterator
            ステータスとその値について反復処理するイテレータ。

        """
        return iter(self._statuses.items())


    def __getitem__(self, status_name):
        """
        ステータスの値を取得する。

        Parameters
        ----------
        status_name : str
            取得するステータスの名前。

        Raises
        ------
        KeyError
            ステータスが未定義の場合。

        Returns
        -------
        any
            ステータスの値。

        """
        if status_name not in self._statuses:
            raise KeyError(f"ステータス '{status_name}' が定義されていません。")
        return self._statuses[status_name]

    def __setitem__(self, status_name, value):
        """
        ステータスの値を設定する。

        Parameters
        ----------
        status_name : str
            設定するステータスの名前。
        value : any
            新しいステータスの値。

        Raises
        ------
        AttributeError
            ステータスが未定義の場合。

        """
        if status_name not in self._initial_status:
            raise AttributeError(f"ステータス '{status_name}' が定義されていません。")
        setattr(self, status_name, value)
        self._statuses[status_name] = value

    def __repr__(self):
        """
        StatusTrackerの文字列表現を返す。

        Returns
        -------
        str
            StatusTrackerの文字列表現。
        """
        status_str = ', '.join([f"{key}: '{value}'" if isinstance(value, str)
                                else f"{key}: {value}"
                                for key, value in self._statuses.items()])
        return f"StatusTracker[{self._id}]({status_str})"
    
if __name__ == "__main__":
    # 初期ステータスを指定して StatusTracker インスタンスを作成する
    initial_statuses = {
        "STATUS": "IDLE",
        "STORAGE_CHECK": "OK",
        "DISK_SPACE": 0.0,
        "CPU_USAGE": 0.0,
        "MEMORY_USAGE": 0.0,
        "DATABASE_CONNECTIONS": "OK",
        "LOG_FILE_SIZE": 0.0,
    }
    tracker = StatusTracker("system1", initial_statuses)

    # ステータスを設定する
    tracker["STATUS"] = "RUNNING"

    # ステータスを取得する
    print(tracker["STATUS"])  # "RUNNING" が出力される

    # 別のステータスを設定する
    tracker.update_status("CPU_USAGE", 0.8)

    # 別のステータスを取得する
    print(tracker.get_status("CPU_USAGE"))  # 0.8 が出力される

    # 未定義のステータスを設定する (AttributeError が発生する)
    try:
        tracker["UNDEFINED_STATUS"] = "ERROR"
    except AttributeError as e:
        print(e)

    # ステータスをループして取得する (各ステータス名と値が出力される)
    for status_name, status_val in tracker:
        print(status_name, ": ", status_val)

    print(tracker)

    # ステータスを初期値にリセットする
    tracker.reset()

    # StatusTracker インスタンスを削除する
    StatusTracker.delete_instance("system1")