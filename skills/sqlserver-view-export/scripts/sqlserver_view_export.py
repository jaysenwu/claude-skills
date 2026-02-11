#!/usr/bin/env python3
"""
SQL Server View Export: List views, search by keyword, and export to CSV.

Usage:
    python sqlserver_view_export.py list [--env /path/to/.env]
    python sqlserver_view_export.py search <keyword> [--env /path/to/.env]
    python sqlserver_view_export.py export <view_name> [output_file] [--env /path/to/.env]
    python sqlserver_view_export.py batch-export <view1> <view2> ... [--env /path/to/.env]

Examples:
    python sqlserver_view_export.py list
    python sqlserver_view_export.py search sales
    python sqlserver_view_export.py export dbo.CustomerView
    python sqlserver_view_export.py batch-export dbo.SalesView dbo.ProductView
"""

import argparse
import csv
import io
import os
import sys

# Force UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    import codecs
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pyodbc
except ImportError:
    print("ERROR: 'pyodbc' package not found. Install with: pip install pyodbc")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("ERROR: 'pandas' package not found. Install with: pip install pandas")
    sys.exit(1)


# ---------------------------------------------------------------------------
# .env parsing
# ---------------------------------------------------------------------------


def parse_env_file(path):
    """Parse a .env file into a dict. Supports comments, blank lines, and quoted values."""
    if not os.path.exists(path):
        raise FileNotFoundError(f".env file not found: {path}")
    env = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            # Strip surrounding quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            env[key] = value
    return env


def load_config(env_path):
    """Load and validate configuration from .env file."""
    env = parse_env_file(env_path)
    required = ["SQL_SERVER", "SQL_DATABASE", "SQL_USER", "SQL_PASSWORD"]
    missing = [k for k in required if k not in env or not env[k]]
    if missing:
        print(f"ERROR: Missing required .env variables: {', '.join(missing)}")
        print(f"Check your .env file at: {env_path}")
        sys.exit(1)

    # Set defaults
    env.setdefault("SQL_PORT", "1433")
    env.setdefault("TRUST_SERVER_CERTIFICATE", "Yes")
    env.setdefault("OUTPUT_DIR", "./exports")

    return env


# ---------------------------------------------------------------------------
# SQL Server connection
# ---------------------------------------------------------------------------


def create_connection(config):
    """Create a pyodbc connection to SQL Server."""
    server = config["SQL_SERVER"]
    database = config["SQL_DATABASE"]
    username = config["SQL_USER"]
    password = config["SQL_PASSWORD"]
    port = config.get("SQL_PORT", "1433")
    trust_cert = config.get("TRUST_SERVER_CERTIFICATE", "Yes")

    # Build connection string - try ODBC Driver 18 first, fall back to 17
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server},{port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate={trust_cert};"
    )

    try:
        conn = pyodbc.connect(connection_string, timeout=30)
        return conn
    except pyodbc.Error as e:
        print(f"ERROR: Failed to connect to SQL Server")
        print(f"Server: {server}:{port}, Database: {database}")
        print(f"Error details: {e}")
        print("\nTroubleshooting:")
        print("1. Verify ODBC Driver 18 for SQL Server is installed")
        print("2. Check server name, port, and credentials")
        print("3. Ensure SQL Server allows remote connections")
        print("4. Verify firewall settings allow access to port", port)
        sys.exit(1)


# ---------------------------------------------------------------------------
# View operations
# ---------------------------------------------------------------------------


def list_views(conn):
    """List all views in the database."""
    query = """
    SELECT
        s.name AS schema_name,
        v.name AS view_name,
        v.create_date,
        v.modify_date
    FROM sys.views v
    INNER JOIN sys.schemas s ON v.schema_id = s.schema_id
    ORDER BY s.name, v.name
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        views = []
        for row in cursor.fetchall():
            views.append({
                "schema": row.schema_name,
                "name": row.view_name,
                "full_name": f"{row.schema_name}.{row.view_name}",
                "created": str(row.create_date),
                "modified": str(row.modify_date)
            })
        return views
    except pyodbc.Error as e:
        print(f"ERROR: Failed to list views: {e}")
        sys.exit(1)


def search_views(conn, keyword):
    """Search for views matching a keyword."""
    query = """
    SELECT
        s.name AS schema_name,
        v.name AS view_name,
        v.create_date,
        v.modify_date
    FROM sys.views v
    INNER JOIN sys.schemas s ON v.schema_id = s.schema_id
    WHERE v.name LIKE ? OR s.name LIKE ?
    ORDER BY s.name, v.name
    """

    search_pattern = f"%{keyword}%"

    try:
        cursor = conn.cursor()
        cursor.execute(query, (search_pattern, search_pattern))
        views = []
        for row in cursor.fetchall():
            views.append({
                "schema": row.schema_name,
                "name": row.view_name,
                "full_name": f"{row.schema_name}.{row.view_name}",
                "created": str(row.create_date),
                "modified": str(row.modify_date)
            })
        return views
    except pyodbc.Error as e:
        print(f"ERROR: Failed to search views: {e}")
        sys.exit(1)


def export_view_to_csv(conn, view_name, output_path):
    """Export a single view to CSV using pyodbc + csv module."""
    # Parse view name (handle schema.view or just view)
    if "." in view_name:
        schema, table = view_name.split(".", 1)
        full_name = f"[{schema}].[{table}]"
    else:
        full_name = f"[{view_name}]"

    query = f"SELECT * FROM {full_name}"

    try:
        print(f"Querying view: {view_name}")
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        # Write CSV with UTF-8 BOM encoding
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for row in rows:
                # Clean each value
                cleaned_row = []
                for val in row:
                    if val is None:
                        cleaned_row.append('')
                    elif isinstance(val, str):
                        # Replace problematic characters
                        cleaned_val = val.encode('utf-8', errors='replace').decode('utf-8')
                        cleaned_row.append(cleaned_val)
                    else:
                        cleaned_row.append(str(val))
                writer.writerow(cleaned_row)

        print(f"✓ Exported {len(rows)} rows to: {output_path}")
        return True
    except pyodbc.Error as e:
        print(f"ERROR: Failed to query view '{view_name}': {e}")
        return False
    except Exception as e:
        print(f"ERROR: Failed to write CSV for '{view_name}': {e}")
        return False


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def view_name_to_filename(view_name):
    """Convert a view name to a safe CSV filename."""
    # Take the last segment (after the last dot) and strip brackets
    name = view_name.split(".")[-1].strip().strip("[").strip("]")
    # Replace any remaining unsafe characters
    safe = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in name)
    return f"{safe}.csv"


def format_view_table(views, title=None, hint=None):
    """Format views as an ASCII table."""
    if not views:
        print("No views found.")
        return

    schema_w = max(max(len(v["schema"]) for v in views), len("Schema"))
    name_w = max(max(len(v["name"]) for v in views), len("View Name"))
    full_w = max(max(len(v["full_name"]) for v in views), len("Full Name"))

    if title:
        print(f"\n{title}")

    sep = f"+{'-' * (schema_w + 2)}+{'-' * (name_w + 2)}+{'-' * (full_w + 2)}+"
    print(sep)
    print(f"| {'Schema':<{schema_w}} | {'View Name':<{name_w}} | {'Full Name':<{full_w}} |")
    print(sep)
    for view in views:
        print(f"| {view['schema']:<{schema_w}} | {view['name']:<{name_w}} | {view['full_name']:<{full_w}} |")
    print(sep)
    print(f"Total: {len(views)} views")

    if hint:
        print(f"\n{hint}")


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def _resolve_env(env_arg):
    """Resolve .env path from argument."""
    env_path = env_arg
    if not os.path.isabs(env_path):
        env_path = os.path.join(os.getcwd(), env_path)
    return env_path


def run_list(args):
    """Handle the list subcommand."""
    config = load_config(_resolve_env(args.env))

    print(f"Connecting to SQL Server: {config['SQL_SERVER']}")
    print(f"Database: {config['SQL_DATABASE']}")

    conn = create_connection(config)
    views = list_views(conn)
    conn.close()

    title = f"Views in database '{config['SQL_DATABASE']}':"
    hint_view = views[0]["full_name"] if views else "dbo.ViewName"
    hint = f"Hint: Export with: sqlserver_view_export export {hint_view}"

    format_view_table(views, title=title, hint=hint)


def run_search(args):
    """Handle the search subcommand."""
    config = load_config(_resolve_env(args.env))
    keyword = args.keyword

    print(f"Connecting to SQL Server: {config['SQL_SERVER']}")
    print(f"Database: {config['SQL_DATABASE']}")
    print(f'Searching for views matching "{keyword}"...')

    conn = create_connection(config)
    views = search_views(conn, keyword)
    conn.close()

    title = f'Found {len(views)} views matching "{keyword}":'
    hint_view = views[0]["full_name"] if views else "dbo.ViewName"
    hint = f"Hint: Export with: sqlserver_view_export export {hint_view}"

    format_view_table(views, title=title, hint=hint)


def run_export(args):
    """Handle the export subcommand."""
    config = load_config(_resolve_env(args.env))
    view_name = args.view_name

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_dir = config.get("OUTPUT_DIR", "./exports")
        filename = view_name_to_filename(view_name)
        output_path = os.path.join(output_dir, filename)

    if not os.path.isabs(output_path):
        output_path = os.path.join(os.getcwd(), output_path)

    print(f"Connecting to SQL Server: {config['SQL_SERVER']}")
    print(f"Database: {config['SQL_DATABASE']}")

    conn = create_connection(config)
    success = export_view_to_csv(conn, view_name, output_path)
    conn.close()

    if success:
        print(f"\n✓ Export complete!")
    else:
        sys.exit(1)


def run_batch_export(args):
    """Handle the batch-export subcommand."""
    config = load_config(_resolve_env(args.env))
    view_names = args.view_names
    output_dir = config.get("OUTPUT_DIR", "./exports")

    if not os.path.isabs(output_dir):
        output_dir = os.path.join(os.getcwd(), output_dir)

    print(f"Connecting to SQL Server: {config['SQL_SERVER']}")
    print(f"Database: {config['SQL_DATABASE']}")
    print(f"Exporting {len(view_names)} views to: {output_dir}\n")

    conn = create_connection(config)

    success_count = 0
    failed_count = 0

    for view_name in view_names:
        filename = view_name_to_filename(view_name)
        output_path = os.path.join(output_dir, filename)

        if export_view_to_csv(conn, view_name, output_path):
            success_count += 1
        else:
            failed_count += 1

    conn.close()

    print(f"\n{'=' * 60}")
    print(f"Batch export complete!")
    print(f"✓ Successful: {success_count}")
    if failed_count > 0:
        print(f"✗ Failed: {failed_count}")
    print(f"Output directory: {output_dir}")

    if failed_count > 0:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="SQL Server View Export: list views, search, and export to CSV",
        epilog="Examples:\n"
               "  sqlserver_view_export.py list\n"
               "  sqlserver_view_export.py search sales\n"
               "  sqlserver_view_export.py export dbo.CustomerView\n"
               "  sqlserver_view_export.py batch-export dbo.View1 dbo.View2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list subcommand
    list_p = subparsers.add_parser("list", help="List all views in the database")
    list_p.add_argument("--env", default=".env", help="Path to .env file (default: .env)")

    # search subcommand
    search_p = subparsers.add_parser("search", help="Search for views by keyword")
    search_p.add_argument("keyword", help="Search keyword (matches schema or view name)")
    search_p.add_argument("--env", default=".env", help="Path to .env file (default: .env)")

    # export subcommand
    export_p = subparsers.add_parser("export", help="Export a single view to CSV")
    export_p.add_argument("view_name", help="View name (e.g. dbo.CustomerView)")
    export_p.add_argument("output", nargs="?", default=None, help="Output CSV file path")
    export_p.add_argument("--env", default=".env", help="Path to .env file (default: .env)")

    # batch-export subcommand
    batch_p = subparsers.add_parser("batch-export", help="Export multiple views to CSV")
    batch_p.add_argument("view_names", nargs="+", help="View names to export (e.g. dbo.View1 dbo.View2)")
    batch_p.add_argument("--env", default=".env", help="Path to .env file (default: .env)")

    args = parser.parse_args()

    if args.command == "list":
        run_list(args)
    elif args.command == "search":
        run_search(args)
    elif args.command == "export":
        run_export(args)
    elif args.command == "batch-export":
        run_batch_export(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
