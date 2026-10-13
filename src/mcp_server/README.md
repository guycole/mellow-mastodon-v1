# Peaker Score MCP Server

This directory contains an MCP server that exposes tools for selecting and updating rows in mastodon_peaker_score.

## What This Server Does

- select_peaker_score: read rows with optional filters
- update_peaker_score: update one row by id

## Prerequisites

- Python 3.10+
- A reachable PostgreSQL database with mastodon_peaker_score
- Connection string in DB_CONN

Default connection string if `DB_CONN` is not set:

postgresql+psycopg2://mastodon_client:batabat@localhost:5432/mastodon

## Setup

From this directory:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run The MCP Server

The server supports both stdio and HTTP transports.

### Stdio mode

```bash
source venv/bin/activate
export DB_CONN='postgresql+psycopg2://USER:PASSWORD@HOST:5432/mastodon'
python peaker_score_server.py --transport stdio
```

### HTTP mode

```bash
source venv/bin/activate
export DB_CONN='postgresql+psycopg2://USER:PASSWORD@HOST:5432/mastodon'
python peaker_score_server.py --transport http --host 127.0.0.1 --port 8000
```

Environment variable equivalents:

- MCP_TRANSPORT: stdio or http
- MCP_HOST: host bind for HTTP mode
- MCP_PORT: port bind for HTTP mode

## MCP Client Configuration Example

Use your MCP client config to launch this server in stdio mode.

```json
{
  "mcpServers": {
    "peaker-score": {
      "command": "/Users/gsc/github/mellow-mastodon-v1/src/mcp_server/venv/bin/python",
      "args": [
        "/Users/gsc/github/mellow-mastodon-v1/src/mcp_server/peaker_score_server.py"
      ],
      "env": {
        "DB_CONN": "postgresql+psycopg2://USER:PASSWORD@HOST:5432/mastodon"
      }
    }
  }
}
```

## Using With Ollama gpt-oss:20b

The model selection is done in your MCP-capable client, not in the server itself.
Set your client model to ollama:gpt-oss:20b (or your client's equivalent naming), and keep this server attached as a tool provider.

## Tool Parameters

### select_peaker_score

- id (optional)
- case_notation (optional)
- crate_name (optional)
- task (optional)
- freq_hz (optional)
- min_freq_hz (optional)
- max_freq_hz (optional)
- sort_by (optional): id_desc, id_asc, peaker_quantity_desc, peaker_quantity_asc
- limit (optional, default 200, capped)

### update_peaker_score

- id (required)
- case_notation (optional)
- crate_name (optional)
- freq_hz (optional)
- peaker_quantity (optional)
- service (optional)
- task (optional)

Returns both before and after row values.
