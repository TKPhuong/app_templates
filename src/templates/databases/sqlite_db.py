from typing import List, Tuple
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class SqliteDB:
    """
    SQLiteデータベースにアクセスするためのクラス。

    Parameters
    ----------
    db_file : str
        SQLiteデータベースのファイルパス。

    Attributes
    ----------
    db_file : str
        SQLiteデータベースのファイルパス。
    tables : dict
        データベース内のテーブル名と列定義のマップ。
    engine : sqlalchemy.engine.Engine
        データベースエンジン。
    Session : sqlalchemy.orm.session.sessionmaker
        セッションを作成するためのsessionmakerオブジェクト。

    """

    def __init__(self, db_file: str):
        """
        SQLiteデータベースのファイルパスを指定して、SqliteDBオブジェクトを作成します。

        Parameters
        ----------
        db_file : str
            SQLiteデータベースのファイルパス。

        """
        self.db_file = db_file
        self.tables = {}
        self.engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
        self.Session = sessionmaker(bind=self.engine)

    def add_table(self, table_name: str, columns: List[Tuple[str, str]]):
        """
        指定されたテーブル名と列定義を使用して、データベース内に新しいテーブルを作成します。

        Parameters
        ----------
        table_name : str
            テーブル名。
        columns : List[Tuple[str, str]]
            列定義のリスト。各要素は、列名とデータ型のタプルです。

        """
        self.tables[table_name] = columns
        with self.get_session() as session:
            column_string = ", ".join([f"{col[0]} {col[1]}" for col in columns])
            session.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_string})")

    def insert(self, table_name: str, values: Tuple):
        """
        指定されたテーブルに、指定された値を持つ新しいレコードを挿入します。

        Parameters
        ----------
        table_name : str
            テーブル名。
        values : Tuple
            新しいレコードの値のタプル。

        """
        with self.get_session() as session:
            value_string = ", ".join([f"'{v}'" for v in values])
            session.execute(f"INSERT INTO {table_name} VALUES ({value_string})")

    def insert_many(self, table_name: str, values: List[Tuple]):
        """
        指定されたテーブルに、複数の新しいレコードを挿入します。

        Parameters
        ----------
        table_name : str
            テーブル名。
        values : List[Tuple]
            新しいレコードの値のリスト。各要素は、列の値のタプル
        """
        with self.get_session() as session:
            column_count = len(self.tables[table_name])

            # 各タプルの値をカンマ区切りの文字列に変換して、括弧で囲んでリストに格納する
            value_strings = []
            for value in values:
                item_strings = [f'"{value[i]}"' for i in range(column_count)]
                value_string = f"({', '.join(item_strings)})"
                value_strings.append(value_string)

            # 各タプルの値をカンマ区切りで結合し、INSERTクエリを実行する
            value_string = ", ".join(value_strings)
            session.execute(f"INSERT INTO {table_name} VALUES {value_string}")

    def select(
        self,
        table_name: str,
        columns: List[str] = None,
        where_clause: str = None,
        order_by: str = None,
        join_clause: str = None,
        limit: int = None,
    ) -> List[Tuple]:
        """
        指定されたテーブルから、指定された条件に一致するレコードを取得します。

        Parameters
        ----------
        table_name : str
            テーブル名。
        columns : List[str], optional
            取得する列名のリスト。デフォルトは全ての列を取得します。
        where_clause : str, optional
            WHERE句の文字列。デフォルトはNoneです。
        order_by : str, optional
            ORDER BY句の文字列。デフォルトはNoneです。
        join_clause : str, optional
            JOIN句の文字列。デフォルトはNoneです。
        limit : int, optional
            取得するレコードの最大数。デフォルトはNoneです。

        Returns
        -------
        List[Tuple]
            指定された条件に一致するレコードのタプルのリスト。

        """
        with self.get_session() as session:
            column_string = "*"
            if columns:
                column_string = ", ".join(columns)
            query = f"SELECT {column_string} FROM {table_name}"
            if join_clause:
                query += f" {join_clause}"
            if where_clause:
                query += f" WHERE {where_clause}"
            if order_by:
                query += f" ORDER BY {order_by}"
            if limit:
                query += f" LIMIT {limit}"
            result = session.execute(query)
            return result.fetchall()

    def update(self, table_name: str, set_clause: str, where_clause: str):
        """
        指定されたテーブル内のレコードを更新します。

        Parameters
        ----------
        table_name : str
            テーブル名。
        set_clause : str
            SET句の文字列。
        where_clause : str
            WHERE句の文字列。

        """
        with self.get_session() as session:
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            session.execute(query)

    def delete(self, table_name: str, where_clause: str):
        """
        指定されたテーブル内のレコードを削除します。

        Parameters
        ----------
        table_name : str
            テーブル名。
        where_clause : str
            WHERE句の文字列。
        """
        with self.get_session() as session:
            query = f"DELETE FROM {table_name} WHERE {where_clause}"
            session.execute(query)

    @contextmanager
    def get_session(self):
        """
        新しいセッションを生成して返します。withブロック内で使用して、自動的にコミットまたはロールバックするようにします。

        Yields
        ------
        Session
            新しいセッションオブジェクト。

        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

           




if __name__ == "__main__":
    import tempfile
    import os
    # 以下はSqliteDBクラスの使用例です。
    with tempfile.TemporaryDirectory() as tmpdir:

        # データベース接続の作成
        db = SqliteDB(os.path.join(tmpdir, "test.db"))

        # テーブルの作成
        db.add_table("users", [("id", "INTEGER PRIMARY KEY"), ("name", "TEXT"), ("email", "TEXT")])
        db.add_table("posts", [("id", "INTEGER PRIMARY KEY"), ("title", "TEXT"), ("content", "TEXT"), ("user_id", "INTEGER")])
        
        # データの挿入
        for i in range(1, 6):
            db.insert("users", (i, f"User {i}", f"user{i}@example.com"))
            db.insert("posts", (i, f"Post {i}", f"Content of post {i}", i))

            # 複数のレコードの挿入
        records = [(7, "Alice", "alice@example.com"), (8, "Bob", "bob@example.com"), (9, "Charlie", "charlie@example.com")]
        db.insert_many("users", records)

        # データの選択
        data = db.select("users", columns=["name", "email"], where_clause="id = 1")
        print(data)

        # データの更新
        db.update("users", set_clause="name = 'Jane Doe'", where_clause="id = 1")
        data = db.select("users", columns=["name", "email"], where_clause="id = 1")
        print(data)

        # 複数のテーブルからのデータの選択
        data = db.select(
            "users u",
            columns=["u.name", "p.title"],
            join_clause="INNER JOIN posts p ON u.id = p.user_id",
            where_clause="u.id = 1"
        )
        print(data)

        # データの削除
        db.delete("users", where_clause="id = 3")

        # ORDER BYとLIMITを使ったデータの選択
        data = db.select(
            "users",
            columns=["name", "email"],
            order_by="name DESC",
            limit=3
        )
        print(data)

        # トランザクション内で複数の操作を実行する例
        with db.get_session() as session:
            session.execute("UPDATE users SET name = 'Alice' WHERE id = 1")
            session.execute("UPDATE users SET email = 'alice@example.com' WHERE id = 1")