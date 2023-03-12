import logging
import logging.handlers
import os


class Logger(logging.Logger):
    def __init__(
        self,
        name="main",
        level="info",
        format="%(asctime)s %(levelname)s %(filename)s %(name)s: %(message)s",
        file_path="./log/log.txt",
        backup_count=18,
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
        logger : NewLogger
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