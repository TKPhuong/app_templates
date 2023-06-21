import logging
import logging.handlers
import os


class Logger(logging.Logger):
    def __init__(
    self,
    name="main",
    level="info",
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(name)s: %(message)s",
    file_path="./log/log.txt",
    backup_count=30,
    rotation="size", 
    max_bytes=1024*10, 
    ):
        """
        新しいロガーを生成する

        Parameters:
        -----------
        name : str, optional
            ロガーの名前。親ロガーからの階層構造を表すドット区切りの名前空間で指定する。
        level : str, optional
            ログの出力レベル。'debug', 'info', 'warning', 'error', 'critical'のいずれかを指定する。
        format : str, optional
            ログの出力フォーマット。Pythonのloggingモジュールのフォーマット文字列を指定する。
        file_path : str, optional
            ログファイルのパス。ログをファイルに書き込む場合に指定する。
        backup_count : int, optional
            ログファイルのバックアップ数。古いログファイルをローテーションする場合に指定する。
        rotation : str, optional
            ファイルローテーションのタイプを指定する。ファイルサイズベースでは設定値を「size」に、時間(日付き)ベースでは「time」に設定する
        max_bytes : int, optional
            ファイルローテーションのタイプがファイルサイズベースの場合に、ファイルサイズの上限を指定する。単位はバイト。
        """
        
        # ロガーを生成し、ログレベルを指定する
        super().__init__(name, level.upper())

        # ログファイルのディレクトリを作成する
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 標準出力用のログハンドラを生成する
        ch = logging.StreamHandler()
        ch.setLevel(level.upper())

        # ログファイル用のローテーションハンドラを生成する
        fh = logging.handlers.TimedRotatingFileHandler(
            file_path,
            encoding="utf-8",
            when="midnight",
            interval=1,
            backupCount=backup_count,
        )
        if rotation.lower() == "time":
            fh = logging.handlers.TimedRotatingFileHandler(
                file_path,
                encoding="utf-8",
                when="midnight",
                interval=1,
                backupCount=backup_count,
            )
        elif rotation.lower() == "size":
            fh = logging.handlers.RotatingFileHandler(
                file_path,
                encoding="utf-8",
                maxBytes=max_bytes,
                backupCount=backup_count,
            )
        else:
            raise ValueError("Invalid rotation type. Choose 'time' or 'size'.")
        fh.setLevel(level.upper())

        # フォーマッタを生成し、ハンドラにセットする
        formatter = logging.Formatter(format)
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # ロガーにハンドラを追加する
        self.addHandler(ch)
        self.addHandler(fh)

    def getChild(self, suffix):
        """
        指定されたsuffixで子ロガーを取得する

        Parameters:
        -----------
        suffix : str
            子ロガーの名前として付加するサフィックス

        Returns:
        --------
        logger : Logger
            指定された名前の子ロガー
        """
        # 子ロガーの名前を生成する
        name = f"{self.name}.{suffix}" if self.name != "root" else suffix

        # 子ロガーがすでに存在する場合は、そのロガーを返す
        if name in self.manager.loggerDict:
            logger = self.manager.loggerDict[name]

        # 子ロガーが存在しない場合は、新しいロガーを生成して返す
        else:
            logger = self.__class__(name)
            logger.manager = self.manager
            logger.parent = self
            logger.level = self.level
            logger.handlers = self.handlers
            logger.propagate = False
            self.manager.loggerDict[name] = logger
        
        return logger
    
if __name__ == "__main__":
    import tempfile

    def sample_log(logger):
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        logger.critical("This is a critical message")

    with tempfile.TemporaryDirectory() as tempdir:
        # Example 1
        logger1 = Logger(file_path=f"{tempdir}/log1.log")
        # Log messages with different log levels
        sample_log(logger1)

        # Example 2
        logger2 = Logger(
            name="custom",
            level="debug",
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            file_path=f"{tempdir}/log2.log",
            backup_count=10,
        )
        sample_log(logger2)

        # Example 3
        parent_logger = Logger(name="parent", file_path=f"{tempdir}/log3.log")
        child_logger1 = parent_logger.getChild("child1")
        child_logger2 = parent_logger.getChild("child2")

        parent_logger.info("This is a message from the parent logger")
        child_logger1.info("This is a message from child logger 1")
        child_logger2.info("This is a message from child logger 2")

        # Example 4
        logger4 = Logger(file_path=f"{tempdir}/log4.log")
        try:
            x = 1 / 0
        except ZeroDivisionError as e:
            logger4.exception(f"An exception occurred: {e}")
        
        # # Processing time testing
        # import time
        # import random
        # import string

        # # generate a random message
        # def generate_random_message(length):
        #     """Generate a random string of fixed length """
        #     return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

        # # How many times to log the message
        # iterations = 1000

        # # List to store time taken for each iteration
        # times = []
        # time_logger = Logger(name="test_time", file_path=f"{tempdir}/log4.log")

        
        # for _ in range(iterations):
        #     # Prepare a random message of length between 10 and 200
        #     message = generate_random_message(random.randint(10, 200))  
        #     # Start time
        #     start = time.time()

        #     # Log your message
        #     time_logger.info(message)

        #     # End time
        #     end = time.time()

        #     # Append time taken to log a message to list
        #     times.append(end - start)

        # # Print average time taken to log a message
        # print(f"Average time taken to log a message: {sum(times) / iterations} seconds")

        # Shut down the logger
        logging.shutdown()