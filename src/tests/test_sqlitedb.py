import pytest
import os.path
import sys

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.databases import SqliteDB

DB_FILE = "test.db"


@pytest.fixture(scope="module")
def test_db():
    db = SqliteDB(DB_FILE)
    db.add_table(
        "users", [("id", "INTEGER PRIMARY KEY"), ("name", "TEXT"), ("age", "INTEGER")]
    )
    db.insert("users", [1, "Alice", 20])
    db.insert("users", [2, "Bob", 25])
    yield db
    os.remove(DB_FILE)


class TestSqliteDB:
    def test_add_table(self, test_db):
        columns = [("id", "INTEGER PRIMARY KEY"), ("name", "TEXT"), ("age", "INTEGER")]
        test_db.add_table("test_table", columns)
        assert "test_table" in test_db.tables
        assert test_db.tables["test_table"] == columns

    def test_insert(self, test_db):
        test_db.insert("users", [3, "Charlie", 30])
        result = test_db.select("users", columns=["name"], where_clause="id = 3")
        assert result == [("Charlie",)]

    def test_select(self, test_db):
        result = test_db.select(
            "users", columns=["name", "age"], where_clause="age > 20"
        )
        assert result == [("Bob", 25), ("Charlie", 30)]

    # @pytest.mark.parametrize(
    #     "columns, where_clause, order_by, limit, expected",
    #     [
    #         (["name", "age"], None, None, None, [("Alice", 20), ("Bob", 25), ("Charlie", 30), ("Dave", 40), ("Frank", 50)]),
    #         (["name"], "age > 25", None, None, [("Bob",), ("Charlie",), ("Dave",), ("Frank",)]),
    #         (["name"], None, "age DESC", None, [("Frank",), ("Dave",), ("Charlie",), ("Bob",), ("Alice",)]),
    #         (["name"], None, None, 3, [("Alice",), ("Bob",), ("Charlie",)]),
    #     ]
    # )
    # def test_select_with_params(self, test_db, columns, where_clause, order_by, limit, expected):
    #     result = test_db.select("users", columns=columns, where_clause=where_clause, order_by=order_by, limit=limit)
    #     assert result == expected

    def test_insert_many(self, test_db):
        data = [
            (4, "Dave", 40),
            (5, "Eve", 45),
            (6, "Frank", 50)
        ]
        test_db.insert_many("users", data)
        result = test_db.select("users", columns=["name"], where_clause="id > 3")
        assert result == [("Dave",), ("Eve",), ("Frank",)]

    def test_update(self, test_db):
        test_db.update("users", "age = 26", "name = 'Bob'")
        result = test_db.select("users", columns=["age"], where_clause="name = 'Bob'")
        assert result == [(26,)]

    def test_delete(self, test_db):
        test_db.delete("users", "name = 'Charlie'")
        result = test_db.select("users", columns=["name"], where_clause="age = 30")
        assert result == []

    def test_join(self, test_db):
        db = test_db
        db.add_table(
            "books",
            [("id", "INTEGER PRIMARY KEY"), ("title", "TEXT"), ("user_id", "INTEGER")],
        )
        db.insert("books", [1, "The Great Gatsby", 1])
        db.insert("books", [2, "Pride and Prejudice", 1])
        db.insert("books", [3, "To Kill a Mockingbird", 2])
        result = db.select(
            "users",
            columns=["name", "title"],
            join_clause="JOIN books ON users.id = books.user_id",
        )
        assert result == [
            ("Alice", "The Great Gatsby"),
            ("Alice", "Pride and Prejudice"),
            ("Bob", "To Kill a Mockingbird"),
        ]
