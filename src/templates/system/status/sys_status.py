class SystemStatus:
    """
    システムステータスを管理するクラス。
    """
    _instance = None

    def __new__(cls, statuses=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if statuses is None:
                cls._instance.statuses = cls.initialize()
            else:
                cls.statuses = statuses
        return cls._instance

    @classmethod
    def initialize(cls):
        return {
            "STORAGE_CHECK": "OK",
            "DISK_SPACE": 0.0,
            "CPU_USAGE": 0.0,
            "MEMORY_USAGE": 0.0,
            "DATABASE_CONNECTIONS": "OK",
            "LOG_FILE_SIZE": 0.0,
        }


    @classmethod
    def reset(cls):
        cls._instance = None

    def update_status(self, status_name, value):
        self.statuses[status_name] = value

    def get_status(self, status_name):
        return self.statuses.get(status_name)

    def __setitem__(self, status_name, value):
        self.statuses[status_name] = value

    def __getitem__(self, status_name):
        return self.statuses.get(status_name)