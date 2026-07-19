#!/usr/bin/env python3
"""
Applies db/schema.sql to a MySQL server via mysql-connector-python.

Used by CI (.github/workflows/ci.yml, the `schema-sql` job) to prove
the hand-written schema actually executes on real MySQL. Deliberately
does NOT shell out to an OS `mysql` CLI binary: on Ubuntu, the
`mysql-client` apt package is a transitional package that actually
installs MariaDB's client, which has a history of failing to
authenticate against MySQL 8's default `caching_sha2_password` plugin.
mysql-connector-python is Oracle's own driver and doesn't have that
problem, and pinning it in requirements-dev.txt means CI always uses a
known-good, reproducible client instead of whatever happens to be
preinstalled on the runner image.
"""

import argparse
import pathlib
import sys

import mysql.connector


def split_statements(sql_text: str) -> list[str]:
    """Splits a .sql file into individual statements on top-level
    semicolons, skipping comment lines and blank lines. Good enough for
    this schema file specifically: it has no stored procedures or
    triggers with semicolons inside their body, which would need a
    smarter DELIMITER-aware parser.

    A statement boundary is decided from the *code* portion of a line
    (everything before an inline `-- comment`), not the raw line —
    several lines in schema.sql end in `...;  -- some comment`, and
    checking the raw line's ending would miss the semicolon and glue
    that statement onto the next one."""
    statements = []
    current_lines = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--") or not stripped:
            continue
        current_lines.append(line)
        code_only = line.split("--", 1)[0].rstrip()
        if code_only.endswith(";"):
            statements.append("\n".join(current_lines))
            current_lines = []
    if current_lines:
        raise ValueError("File ended mid-statement — missing a trailing semicolon somewhere.")
    return statements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sql_file", type=pathlib.Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    args = parser.parse_args()

    sql_text = args.sql_file.read_text(encoding="utf-8")
    statements = split_statements(sql_text)

    conn = mysql.connector.connect(host=args.host, port=args.port, user=args.user, password=args.password)
    cursor = conn.cursor()
    try:
        for statement in statements:
            cursor.execute(statement)
    except mysql.connector.Error as exc:
        print(f"Failed on statement:\n{statement}\n", file=sys.stderr)
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Applied {len(statements)} statements from {args.sql_file}")


if __name__ == "__main__":
    main()
