from sqlalchemy import create_engine, text
from pathlib import Path

# Database URL (adjust if needed)
DB_URL = "sqlite:///CIF-AI/data/customer_ai.db"

# Output file
OUTPUT_FILE = Path("db_dump.txt")

engine = create_engine(DB_URL)

def write_table(conn, table_name, file):
    file.write(f"\n{'=' * 80}\n")
    file.write(f"TABLE: {table_name}\n")
    file.write(f"{'=' * 80}\n")

    # Fetch rows
    result = conn.execute(text(f"SELECT * FROM {table_name}"))
    rows = result.fetchall()

    if not rows:
        file.write("(no rows)\n")
        return

    # Column names
    columns = result.keys()
    col_widths = {col: max(len(col), 20) for col in columns}

    # Adjust width based on content
    for row in rows:
        for col, val in zip(columns, row):
            col_widths[col] = max(col_widths[col], len(str(val)))

    # Header
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    separator = "-+-".join("-" * col_widths[col] for col in columns)

    file.write(header + "\n")
    file.write(separator + "\n")

    # Rows
    for row in rows:
        line = " | ".join(str(val).ljust(col_widths[col]) for col, val in zip(columns, row))
        file.write(line + "\n")


with engine.connect() as conn, open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("CUSTOMER AI – DATABASE DUMP\n")
    f.write("=" * 80 + "\n")

    write_table(conn, "messages", f)
    write_table(conn, "escalations", f)
    write_table(conn, "analytics_events", f)

print(f"Database exported successfully to: {OUTPUT_FILE.resolve()}")

