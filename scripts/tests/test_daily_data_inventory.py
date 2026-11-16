import sqlite3

from daily_data_inventory import rows


def test_rows_returns_named_columns():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("CREATE TABLE sample(day TEXT, value INTEGER)")
    connection.execute("INSERT INTO sample VALUES ('2026-01-01', 2)")
    assert rows(connection, "SELECT * FROM sample") == [{"day": "2026-01-01", "value": 2}]
