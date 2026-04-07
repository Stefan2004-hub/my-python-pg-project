"""Generate PostgreSQL DDL from SQLAlchemy model metadata."""

from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from app.models import Base


OUTPUT_FILE = Path("generated_schema.sql")


def main() -> None:
    """Write CREATE TABLE statements generated from ORM metadata."""
    print("Generating PostgreSQL DDL from Python models...")

    statements = [
        "-- Generated from SQLAlchemy model metadata.",
        "-- Review before using as a database initialization or migration script.",
        "",
    ]
    dialect = postgresql.dialect()

    for table in Base.metadata.sorted_tables:
        statements.append(f"{CreateTable(table).compile(dialect=dialect)};")
        statements.append("")

    OUTPUT_FILE.write_text("\n".join(statements), encoding="utf-8")
    print(f"Success! Created {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
