#!/usr/bin/env python3
"""
Test script for mssql-mcp server integration.
This script provides a simple interface for calling the mssql-mcp server from Python.
"""

import subprocess
import json
import sys
import time


def run_command(command):
    """Run a subprocess command and return the output."""
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True
        )
        stdout, stderr = process.communicate(timeout=30)
        return process.returncode, stdout.strip(), stderr.strip()
    except Exception as e:
        return -1, "", str(e)


def list_tables():
    """List all tables in the database."""
    print("Listing all tables...")
    command = """echo '{
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/call",
        "params": {
            "name": "list_table",
            "arguments": {}
        }
    }' | node -e '
        const readline = require("readline");
        const { spawn } = require("child_process");

        const server = spawn("cmd", [
            "/c",
            "node",
            "C:/Users/JSW023/Downloads/SQL-AI-samples-main/SQL-AI-samples-main/MssqlMcp/Node/dist/index.js"
        ], {
            env: {
                ...process.env,
                SERVER_NAME: "apsosharesql06X",
                DATABASE_NAME: "FEADB",
                SQL_USER: "Apabi_view",
                SQL_PASSWORD: "J[4C7>(\"Ns&#<?3$",
                TRUST_SERVER_CERTIFICATE: "true"
            }
        });

        let output = "";
        let errorOutput = "";

        server.stdout.on("data", (data) => {
            output += data.toString();
        });

        server.stderr.on("data", (data) => {
            errorOutput += data.toString();
        });

        server.on("close", (code) => {
            if (code !== 0) {
                console.error("Error:", errorOutput);
            } else {
                console.log(output);
            }
            process.exit(code);
        });

        server.stdin.write(JSON.stringify({
            "jsonrpc": "2.0",
            "id": "1",
            "method": "tools/call",
            "params": {
                "name": "list_table",
                "arguments": {}
            }
        }) + "\\n");

        setTimeout(() => {
            server.kill();
            console.log("Timeout.");
        }, 10000);
    '
    """
    return run_command(command)


def describe_table(table_name):
    """Describe the schema of a specific table."""
    print(f"Describing table: {table_name}")
    command = f"""echo '{{
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/call",
        "params": {{
            "name": "describe_table",
            "arguments": {{
                "tableName": "{table_name}"
            }}
        }}
    }}' | node -e '
        const readline = require("readline");
        const {{ spawn }} = require("child_process");

        const server = spawn("cmd", [
            "/c",
            "node",
            "C:/Users/JSW023/Downloads/SQL-AI-samples-main/SQL-AI-samples-main/MssqlMcp/Node/dist/index.js"
        ], {{
            env: {{
                ...process.env,
                SERVER_NAME: "apsosharesql06X",
                DATABASE_NAME: "FEADB",
                SQL_USER: "Apabi_view",
                SQL_PASSWORD: "J[4C7>(\"Ns&#<?3$",
                TRUST_SERVER_CERTIFICATE: "true"
            }}
        }});

        let output = "";
        let errorOutput = "";

        server.stdout.on("data", (data) => {{
            output += data.toString();
        }});

        server.stderr.on("data", (data) => {{
            errorOutput += data.toString();
        }});

        server.on("close", (code) => {{
            if (code !== 0) {{
                console.error("Error:", errorOutput);
            }} else {{
                console.log(output);
            }}
            process.exit(code);
        }});

        server.stdin.write(JSON.stringify({{
            "jsonrpc": "2.0",
            "id": "1",
            "method": "tools/call",
            "params": {{
                "name": "describe_table",
                "arguments": {{
                    "tableName": "{table_name}"
                }}
            }}
        }}) + "\\n");

        setTimeout(() => {{
            server.kill();
            console.log("Timeout.");
        }}, 10000);
    '
    """
    return run_command(command)


def read_data(query):
    """Execute a SELECT query on a table."""
    print(f"Executing query: {query}")
    # Escape quotes in query
    escaped_query = query.replace('"', '\\"')
    command = f"""echo '{{
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/call",
        "params": {{
            "name": "read_data",
            "arguments": {{
                "query": "{escaped_query}"
            }}
        }}
    }}' | node -e '
        const readline = require("readline");
        const {{ spawn }} = require("child_process");

        const server = spawn("cmd", [
            "/c",
            "node",
            "C:/Users/JSW023/Downloads/SQL-AI-samples-main/SQL-AI-samples-main/MssqlMcp/Node/dist/index.js"
        ], {{
            env: {{
                ...process.env,
                SERVER_NAME: "apsosharesql06X",
                DATABASE_NAME: "FEADB",
                SQL_USER: "Apabi_view",
                SQL_PASSWORD: "J[4C7>(\"Ns&#<?3$",
                TRUST_SERVER_CERTIFICATE: "true"
            }}
        }});

        let output = "";
        let errorOutput = "";

        server.stdout.on("data", (data) => {{
            output += data.toString();
        }});

        server.stderr.on("data", (data) => {{
            errorOutput += data.toString();
        }});

        server.on("close", (code) => {{
            if (code !== 0) {{
                console.error("Error:", errorOutput);
            }} else {{
                console.log(output);
            }}
            process.exit(code);
        }});

        server.stdin.write(JSON.stringify({{
            "jsonrpc": "2.0",
            "id": "1",
            "method": "tools/call",
            "params": {{
                "name": "read_data",
                "arguments": {{
                    "query": "{escaped_query}"
                }}
            }}
        }}) + "\\n");

        setTimeout(() => {{
            server.kill();
            console.log("Timeout.");
        }}, 10000);
    '
    """
    return run_command(command)


def main():
    if len(sys.argv) < 2:
        print("Usage: python mssql-mcp.py <command> [args]")
        print("\nCommands:")
        print("  list-tables              List all tables")
        print("  describe <table_name>    Describe table schema")
        print("  query <sql_query>        Execute a SELECT query")
        print("\nExamples:")
        print("  python mssql-mcp.py list-tables")
        print("  python mssql-mcp.py describe T_CINS_dwell")
        print('  python mssql-mcp.py query "SELECT TOP 10 * FROM dbo.T_CINS_dwell"')
        return

    command = sys.argv[1]

    if command == "list-tables":
        returncode, stdout, stderr = list_tables()
    elif command == "describe":
        if len(sys.argv) < 3:
            print("Error: Table name is required")
            return
        returncode, stdout, stderr = describe_table(sys.argv[2])
    elif command == "query":
        if len(sys.argv) < 3:
            print("Error: SQL query is required")
            return
        returncode, stdout, stderr = read_data(sys.argv[2])
    else:
        print(f"Error: Unknown command '{command}'")
        return

    if returncode != 0:
        print(f"Error ({returncode}): {stderr}")
    else:
        # Parse JSON response
        try:
            data = json.loads(stdout)
            print(json.dumps(data, indent=2))
        except:
            print(stdout)


if __name__ == "__main__":
    main()