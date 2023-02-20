from datetime import datetime
import os.path
import sys

# add the parent directory of the current file to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from templates.databases.sqlite_db.sqlite_db import SqliteDB


class InventorySystem:
    def __init__(self):
        # create a database object
        self.db = SqliteDB("inventory.db")

        # create the products table if it doesn't exist
        self.db.add_table(
            "products",
            [
                ("id", "INTEGER PRIMARY KEY"),
                ("name", "TEXT NOT NULL"),
                ("price", "REAL NOT NULL"),
                ("stock", "INTEGER NOT NULL"),
            ],
        )

        # create the sales table if it doesn't exist
        self.db.add_table(
            "sales",
            [
                ("id", "INTEGER PRIMARY KEY"),
                ("product_id", "INTEGER NOT NULL"),
                ("quantity", "INTEGER NOT NULL"),
                ("timestamp", "TEXT NOT NULL"),
                ("price", "REAL NOT NULL"),
                ("total", "REAL NOT NULL"),
                ("created_at", "TEXT NOT NULL"),
            ],
        )

    def add_product(self, name, price, stock):
        # insert a new product into the database
        self.db.insert("products", (None, name, price, stock))

    def sell_product(self, product_id, quantity):
        # get the product's price and stock
        result = self.db.select(
            "products", columns=["price", "stock"], where_clause=f"id = {product_id}"
        )[0]
        price, stock = result

        # calculate the total price of the sale
        total = price * quantity

        # update the product's stock
        new_stock = stock - quantity
        self.db.update(
            "products",
            set_clause=f"stock = {new_stock}",
            where_clause=f"id = {product_id}",
        )

        # insert a new sale into the database
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.insert(
            "sales",
            (
                None,
                product_id,
                quantity,
                timestamp,
                price,
                total,
                created_at,
            ),
        )

    def get_sales_report(self):
        join_clause = "JOIN products ON sales.product_id = products.id"
        report = self.db.select(
            "sales",
            columns=[
                "sales.id",
                "products.name",
                "sales.quantity",
                "sales.timestamp",
                "sales.price",
                "sales.total",
                "sales.created_at",
            ],
            join_clause=join_clause,
        )
        return report


if __name__ == "__main__":
    # create an instance of the inventory system
    inventory_system = InventorySystem()

    # add two products to the inventory
    inventory_system.add_product("Apple", 0.5, 100)
    inventory_system.add_product("Banana", 1.0, 50)

    # sell 50 apples and 75 bananas
    inventory_system.sell_product(1, 50)
    inventory_system.sell_product(2, 75)

    # retrieve a report of all sales
    report = inventory_system.get_sales_report()
    print(report)
