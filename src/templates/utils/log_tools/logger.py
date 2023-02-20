import logging
import logging.handlers
import os


class Logger:
    def __init__(
        self,
        level="info",
        format="%(asctime)s %(levelname)s %(filename)s %(name)s: %(message)s",
        file_path="./log/log.txt",
        backup_count=18,
    ):
        # ロガーを生成し、ログレベルを指定する
        self._logger = logging.getLogger()
        self._logger.setLevel(level.upper())

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
        self._logger.addHandler(ch)
        self._logger.addHandler(fh)

    def get_logger(self, name=None):
        # 子ロガーを生成する.名前を指定しない場合は、親ロガー自体が返される
        return self._logger.getChild(name) if name else self._logger
