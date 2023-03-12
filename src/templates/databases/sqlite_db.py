from typing import List, Tuple
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class SqliteDB:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.tables = {}
        self.engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
        self.Session = sessionmaker(bind=self.engine)

    def add_table(self, table_name: str, columns: List[Tuple[str, str]]):
        self.tables[table_name] = columns
        with self.get_session() as session:
            column_string = ", ".join([f"{col[0]} {col[1]}" for col in columns])
            session.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_string})")

    def insert(self, table_name: str, values: Tuple):
        with self.get_session() as session:
            value_string = ", ".join([f"'{v}'" for v in values])
            session.execute(f"INSERT INTO {table_name} VALUES ({value_string})")

    def select(
        self,
        table_name: str,
        columns: List[str] = None,
        where_clause: str = None,
        order_by: str = None,
        join_clause: str = None,
        limit: int = None,
    ) -> List[Tuple]:
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
        with self.get_session() as session:
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            session.execute(query)

    def delete(self, table_name: str, where_clause: str):
        with self.get_session() as session:
            query = f"DELETE FROM {table_name} WHERE {where_clause}"
            session.execute(query)

    @contextmanager
    def get_session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
