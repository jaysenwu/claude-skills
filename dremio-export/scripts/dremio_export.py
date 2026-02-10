#!/usr/bin/env python3
"""
Dremio Export: Query views, list catalog, and search.

Usage:
    python dremio_export.py export <view_name> [output_file] [--env /path/to/.env]
    python dremio_export.py list [path] [--recursive] [--env /path/to/.env]
    python dremio_export.py search <keyword> [--env /path/to/.env]

    # Legacy (backward compatible):
    python dremio_export.py <view_name> [output_file] [--env /path/to/.env]

Examples:
    python dremio_export.py export my_space.my_view
    python dremio_export.py list my_space
    python dremio_export.py list my_space --recursive
    python dremio_export.py search sales
"""

import argparse
import csv
import os
import sys
import time
import urllib.parse

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package not found. Install with: pip3 install requests")
    sys.exit(1)


# ---------------------------------------------------------------------------
# .env parsing
# ---------------------------------------------------------------------------


def parse_env_file(path):
    """Parse a .env file into a dict. Supports comments, blank lines, and quoted values."""
    if not os.path.exists(path):
        raise FileNotFoundError(f".env file not found: {path}")
    env = {}
    with open(path, "r") as f:
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
    required = ["DREMIO_BASE_URL", "DREMIO_API_KEY"]
    missing = [k for k in required if k not in env or not env[k]]
    if missing:
        print(f"ERROR: Missing required .env variables: {', '.join(missing)}")
        print(f"Check your .env file at: {env_path}")
        sys.exit(1)
    # Strip trailing slash from base URL
    env["DREMIO_BASE_URL"] = env["DREMIO_BASE_URL"].rstrip("/")
    return env


# ---------------------------------------------------------------------------
# Dremio API functions
# ---------------------------------------------------------------------------


def _auth_header(api_key):
    """Return the Authorization header dict for Dremio Software using API key (PAT)."""
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def submit_query(base_url, token, view_name, sql_override=None):
    """Submit a SQL query to Dremio and return the job ID."""
    url = f"{base_url}/api/v3/sql"
    if sql_override:
        sql = sql_override
    else:
        sql = f"SELECT * FROM {view_name}"
    try:
        resp = requests.post(
            url, json={"sql": sql}, headers=_auth_header(token), timeout=30
        )
    except requests.RequestException as e:
        print(f"ERROR: Failed to submit query: {e}")
        sys.exit(1)
    if not resp.ok:
        print(f"ERROR: Query submission failed (HTTP {resp.status_code})")
        try:
            detail = resp.json().get("errorMessage", resp.text)
        except Exception:
            detail = resp.text
        print(f"Detail: {detail}")
        sys.exit(1)
    return resp.json()["id"]


def wait_for_job(base_url, token, job_id, timeout=300, poll_interval=1):
    """Poll job status until COMPLETED, FAILED, or CANCELED."""
    url = f"{base_url}/api/v3/job/{job_id}"
    start = time.time()
    terminal_states = {"COMPLETED", "FAILED", "CANCELED"}
    while True:
        try:
            resp = requests.get(url, headers=_auth_header(token), timeout=30)
        except requests.RequestException as e:
            print(f"ERROR: Failed to check job status: {e}")
            sys.exit(1)
        if not resp.ok:
            print(f"ERROR: Job status check failed (HTTP {resp.status_code})")
            sys.exit(1)
        data = resp.json()
        state = data.get("jobState", "UNKNOWN")
        if state in terminal_states:
            if state == "COMPLETED":
                return data
            elif state == "FAILED":
                msg = data.get("errorMessage", "Unknown error")
                print(f"ERROR: Query failed: {msg}")
                sys.exit(1)
            elif state == "CANCELED":
                print("ERROR: Query was canceled.")
                sys.exit(1)
        elapsed = time.time() - start
        if elapsed >= timeout:
            print(f"ERROR: Query timed out after {timeout}s (state: {state})")
            sys.exit(1)
        time.sleep(poll_interval)


def fetch_all_results(base_url, token, job_id, row_count, page_size=500):
    """Fetch all result rows with pagination. Returns (columns, rows)."""
    columns = []
    all_rows = []
    offset = 0
    while offset <= max(row_count - 1, 0):
        url = (
            f"{base_url}/api/v3/job/{job_id}/results"
            f"?offset={offset}&limit={page_size}"
        )
        try:
            resp = requests.get(url, headers=_auth_header(token), timeout=60)
        except requests.RequestException as e:
            print(f"ERROR: Failed to fetch results at offset {offset}: {e}")
            sys.exit(1)
        if not resp.ok:
            print(f"ERROR: Result fetch failed (HTTP {resp.status_code})")
            sys.exit(1)
        data = resp.json()
        # Extract column names from schema on first page
        if not columns and "schema" in data:
            columns = [field["name"] for field in data["schema"]]
        rows = data.get("rows", [])
        all_rows.extend(rows)
        if len(rows) < page_size:
            break
        offset += page_size
    # Handle zero-row case: still extract columns from schema
    if not columns and row_count == 0:
        url = f"{base_url}/api/v3/job/{job_id}/results?offset=0&limit=1"
        try:
            resp = requests.get(url, headers=_auth_header(token), timeout=60)
            if resp.ok:
                data = resp.json()
                if "schema" in data:
                    columns = [field["name"] for field in data["schema"]]
        except requests.RequestException:
            pass
    return columns, all_rows


# ---------------------------------------------------------------------------
# CSV writing
# ---------------------------------------------------------------------------


def write_csv(columns, rows, output_path):
    """Write columns and rows to a CSV file."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def view_name_to_filename(view_name):
    """Convert a Dremio view name to a safe CSV filename."""
    # Take the last segment (after the last dot) and strip quotes
    name = view_name.split(".")[-1].strip().strip('"').strip("'")
    # Replace any remaining unsafe characters
    safe = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in name)
    return f"{safe}.csv"


# ---------------------------------------------------------------------------
# Catalog API functions
# ---------------------------------------------------------------------------


def _parse_path(path):
    """Parse a user-provided path into segments.

    Handles:
        "my_space.my_folder"             -> ["my_space", "my_folder"]
        "my_space/my_folder"             -> ["my_space", "my_folder"]
        '"My Space"."My Folder"'         -> ["My Space", "My Folder"]
    """
    if "/" in path:
        return [seg.strip().strip('"').strip("'") for seg in path.split("/") if seg.strip()]
    if '"' in path:
        segments = []
        current = ""
        in_quotes = False
        for ch in path:
            if ch == '"':
                in_quotes = not in_quotes
            elif ch == "." and not in_quotes:
                if current:
                    segments.append(current)
                    current = ""
            else:
                current += ch
        if current:
            segments.append(current)
        return segments
    return path.split(".")


def get_catalog_by_path(base_url, token, path_segments):
    """Get a catalog item by path segments."""
    encoded = "/".join(urllib.parse.quote(seg, safe="") for seg in path_segments)
    url = f"{base_url}/api/v3/catalog/by-path/{encoded}"
    try:
        resp = requests.get(url, headers=_auth_header(token), timeout=30)
    except requests.RequestException as e:
        print(f"ERROR: Failed to access catalog: {e}")
        sys.exit(1)
    if not resp.ok:
        path_str = ".".join(path_segments)
        print(f"ERROR: Could not find '{path_str}' in catalog (HTTP {resp.status_code})")
        try:
            detail = resp.json().get("errorMessage", resp.text)
        except Exception:
            detail = resp.text
        print(f"Detail: {detail}")
        sys.exit(1)
    return resp.json()


def list_catalog_items(base_url, token, path=None, recursive=False):
    """List catalog items (views, tables, folders) under a path or at root."""
    if path:
        path_segments = _parse_path(path)
        data = get_catalog_by_path(base_url, token, path_segments)
        children = data.get("children", [])
    else:
        url = f"{base_url}/api/v3/catalog"
        try:
            resp = requests.get(url, headers=_auth_header(token), timeout=30)
        except requests.RequestException as e:
            print(f"ERROR: Failed to list catalog: {e}")
            sys.exit(1)
        if not resp.ok:
            print(f"ERROR: Failed to list catalog (HTTP {resp.status_code})")
            sys.exit(1)
        data = resp.json()
        children = data.get("data", [])

    items = []
    for child in children:
        child_type = child.get("type", "")
        container_type = child.get("containerType", "")
        dataset_type = child.get("datasetType", "")
        child_path = child.get("path", [])
        name = child_path[-1] if child_path else child.get("name", "?")
        path_str = ".".join(child_path) if child_path else name

        if child_type == "DATASET":
            kind = "VIEW" if dataset_type == "VIRTUAL" else dataset_type or "DATASET"
            items.append({"name": name, "path": path_str, "type": kind})
        elif child_type == "CONTAINER":
            if recursive:
                sub_items = list_catalog_items(base_url, token, path_str, recursive=True)
                items.extend(sub_items)
            else:
                items.append({"name": name, "path": path_str, "type": container_type or "CONTAINER"})

    return items


def search_catalog(base_url, token, keyword):
    """Search for views/tables matching a keyword using INFORMATION_SCHEMA."""
    safe_keyword = keyword.replace("'", "''").lower()
    sql = (
        "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE "
        'FROM INFORMATION_SCHEMA."TABLES" '
        f"WHERE LOWER(TABLE_NAME) LIKE '%{safe_keyword}%' "
        f"OR LOWER(TABLE_SCHEMA) LIKE '%{safe_keyword}%' "
        "ORDER BY TABLE_SCHEMA, TABLE_NAME"
    )
    job_id = submit_query(base_url, token, None, sql_override=sql)
    job_data = wait_for_job(base_url, token, job_id)
    row_count = job_data.get("rowCount", 0)
    columns, rows = fetch_all_results(base_url, token, job_id, row_count)

    items = []
    for row in rows:
        schema = row.get("TABLE_SCHEMA", "")
        name = row.get("TABLE_NAME", "")
        ttype = row.get("TABLE_TYPE", "")
        kind = "VIEW" if ttype == "VIEW" else ttype
        items.append({
            "name": name,
            "path": f"{schema}.{name}" if schema else name,
            "type": kind,
        })
    return items


def format_catalog_table(items, title=None, hint=None):
    """Format catalog items as an ASCII table."""
    if not items:
        print("No items found.")
        return

    name_w = max(max(len(i["name"]) for i in items), len("Name"))
    path_w = max(max(len(i["path"]) for i in items), len("Path"))
    type_w = max(max(len(i["type"]) for i in items), len("Type"))

    if title:
        print(f"\n{title}")

    sep = f"+{'-' * (name_w + 2)}+{'-' * (path_w + 2)}+{'-' * (type_w + 2)}+"
    print(sep)
    print(f"| {'Name':<{name_w}} | {'Path':<{path_w}} | {'Type':<{type_w}} |")
    print(sep)
    for item in items:
        print(f"| {item['name']:<{name_w}} | {item['path']:<{path_w}} | {item['type']:<{type_w}} |")
    print(sep)
    print(f"Total: {len(items)} items")

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


def run_export(args):
    """Handle the export subcommand."""
    output_path = args.output or view_name_to_filename(args.view_name)
    if not os.path.isabs(output_path):
        output_path = os.path.join(os.getcwd(), output_path)

    config = load_config(_resolve_env(args.env))
    base_url = config["DREMIO_BASE_URL"]
    api_key = config["DREMIO_API_KEY"]

    sql = f"SELECT * FROM {args.view_name}"
    print(f"Connecting to Dremio at {base_url}...")
    print(f"Executing: {sql}")
    job_id = submit_query(base_url, api_key, args.view_name)
    print(f"Job submitted: {job_id}")

    print("Waiting for query to complete...")
    job_data = wait_for_job(base_url, api_key, job_id, timeout=args.timeout)
    row_count = job_data.get("rowCount", 0)
    print(f"Query completed. Rows: {row_count}")

    if row_count > 0:
        print("Fetching results...")
        columns, rows = fetch_all_results(base_url, api_key, job_id, row_count)
    else:
        columns, rows = fetch_all_results(base_url, api_key, job_id, 0)

    write_csv(columns, rows, output_path)
    print(f"CSV saved: {output_path}")
    print(f"Total rows: {len(rows)}, Columns: {len(columns)}")


def run_list(args):
    """Handle the list subcommand."""
    config = load_config(_resolve_env(args.env))
    base_url = config["DREMIO_BASE_URL"]
    api_key = config["DREMIO_API_KEY"]

    path = args.path
    recursive = args.recursive

    print(f"Connecting to Dremio at {base_url}...")
    if path:
        print(f'Listing items in "{path}"' + (" (recursive)" if recursive else "") + "...")
    else:
        print("Listing root catalog items...")

    items = list_catalog_items(base_url, api_key, path, recursive=recursive)

    title = f'Items in "{path}":' if path else "Root catalog items:"
    hint_path = items[0]["path"] if items else "space.view_name"
    hint = f"Hint: Export with: dremio_export.sh export '{hint_path}'"

    format_catalog_table(items, title=title, hint=hint)


def run_search(args):
    """Handle the search subcommand."""
    config = load_config(_resolve_env(args.env))
    base_url = config["DREMIO_BASE_URL"]
    api_key = config["DREMIO_API_KEY"]

    keyword = args.keyword
    print(f"Connecting to Dremio at {base_url}...")
    print(f'Searching for "{keyword}"...')

    items = search_catalog(base_url, api_key, keyword)

    title = f'Found {len(items)} items matching "{keyword}":'
    hint_path = items[0]["path"] if items else "space.view_name"
    hint = f"Hint: Export with: dremio_export.sh export '{hint_path}'"

    format_catalog_table(items, title=title, hint=hint)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    # Backward compatibility: if first arg is not a known subcommand, treat as export
    known_commands = {"export", "list", "search"}
    if len(sys.argv) > 1 and sys.argv[1] not in known_commands and not sys.argv[1].startswith("-"):
        sys.argv.insert(1, "export")

    parser = argparse.ArgumentParser(
        description="Dremio Export: query views, list catalog, and search",
        epilog="Examples:\n"
               "  dremio_export.py export my_space.my_view output.csv\n"
               "  dremio_export.py list my_space\n"
               "  dremio_export.py search sales\n"
               "  dremio_export.py my_space.my_view  (legacy, same as export)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # export subcommand
    export_p = subparsers.add_parser("export", help="Export a Dremio view to CSV")
    export_p.add_argument("view_name", help="Dremio view path (e.g. my_space.my_view)")
    export_p.add_argument("output", nargs="?", default=None, help="Output CSV file path")
    export_p.add_argument("--env", default=".env", help="Path to .env file (default: .env)")
    export_p.add_argument("--timeout", type=int, default=300, help="Query timeout in seconds (default: 300)")

    # list subcommand
    list_p = subparsers.add_parser("list", help="List views in a container (space/folder)")
    list_p.add_argument("path", nargs="?", default=None, help="Container path (e.g. my_space or my_space.my_folder)")
    list_p.add_argument("--recursive", "-r", action="store_true", help="Recursively list all items")
    list_p.add_argument("--env", default=".env", help="Path to .env file (default: .env)")

    # search subcommand
    search_p = subparsers.add_parser("search", help="Search for views by keyword")
    search_p.add_argument("keyword", help="Search keyword")
    search_p.add_argument("--env", default=".env", help="Path to .env file (default: .env)")

    args = parser.parse_args()

    if args.command == "export":
        run_export(args)
    elif args.command == "list":
        run_list(args)
    elif args.command == "search":
        run_search(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
