import sqlite3

class SqliteDB:
    """
    SQLiteデータベースと対話するためのクラスです。
    """
    def __init__(self, db_file):
        """
        SqliteDBクラスのコンストラクタです。

        :param db_file: 接続するデータベースファイルのファイル名です。
        """
        self.db_file = db_file
        self.tables = {}

    def add_table(self, table_name, columns):
        """
        データベースにテーブルを追加します。

        :param table_name: 追加するテーブルの名前です。
        :param columns: 各タプルが列名と列型のペアであるタプルのリストです。
        """
        self.tables[table_name] = columns

        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            column_string = ", ".join([f"{col[0]} {col[1]}" for col in columns])
            c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_string})")

    def insert(self, table_name, values):
        """
        指定されたテーブルに行を挿入します。

        :param table_name: 挿入するテーブルの名前です。
        :param values: テーブル内の列の順序で挿入する値のリストです。
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            value_string = ", ".join(["?" for _ in values])
            c.execute(f"INSERT INTO {table_name} VALUES ({value_string})", values)

    def select(self, table_name, columns=None, where_clause=None, order_by=None, join_clause=None):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
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
            c.execute(query)
            return c.fetchall()

    def update(self, table_name, set_clause, where_clause):
        """
        指定されたテーブルでUPDATEクエリを実行します。

        :param table_name: クエリを実行するテーブルの名前です。
        :param set_clause: クエリのSET句
        :param where_clause: クエリのWHERE句を表す文字列です。
    """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            c.execute(query)

    def delete(self, table_name, where_clause):
        """
        指定されたテーブルでDELETEクエリを実行します。

        :param table_name: クエリを実行するテーブルの名前です。
        :param where_clause: クエリのWHERE句を表す文字列です。
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            query = f"DELETE FROM {table_name} WHERE {where_clause}"
            c.execute(query)