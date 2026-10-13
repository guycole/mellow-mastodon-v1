"""MCP server for selecting and updating mastodon_peaker_score rows."""

from __future__ import annotations

import argparse
import os
from dataclasses import asdict, dataclass
from typing import Any

from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine
from sqlalchemy import text

DEFAULT_DB_CONN = (
    "postgresql+psycopg2://mastodon_client:batabat@localhost:5432/mastodon"
)
DEFAULT_LIMIT = 200
MAX_LIMIT = 1000

mcp = FastMCP("peaker-score-mcp")


@dataclass(slots=True)
class PeakerScoreRow:
    id: int
    case_notation: str
    crate_name: str
    freq_hz: int
    peaker_quantity: int
    service: str
    task: str


def _db_conn() -> str:
    return os.environ.get("DB_CONN", DEFAULT_DB_CONN)


def _engine():
    return create_engine(_db_conn(), pool_pre_ping=True)


def _row_to_model(row: Any) -> PeakerScoreRow:
    return PeakerScoreRow(
        id=int(row.id),
        case_notation=str(row.case_notation),
        crate_name=str(row.crate_name),
        freq_hz=int(row.freq_hz),
        peaker_quantity=int(row.peaker_quantity),
        service=str(row.service),
        task=str(row.task),
    )


def _normalize_sort_by(candidate: str) -> str:
    value = (candidate or "").strip().lower()
    allowed = {
        "id_desc": "id DESC",
        "id_asc": "id ASC",
        "peaker_quantity_desc": "peaker_quantity DESC",
        "peaker_quantity_asc": "peaker_quantity ASC",
    }

    order = allowed.get(value)
    if order is None:
        raise ValueError(
            "sort_by must be one of: id_desc, id_asc, peaker_quantity_desc, peaker_quantity_asc"
        )

    return order


def _normalize_transport(candidate: str) -> str:
    value = (candidate or "").strip().lower()

    aliases = {
        "http": "streamable-http",
        "streamable_http": "streamable-http",
        "streamable-http": "streamable-http",
        "stdio": "stdio",
    }

    normalized = aliases.get(value)
    if normalized is None:
        raise ValueError(
            "MCP_TRANSPORT must be one of: stdio, http, streamable-http"
        )

    return normalized


def _run_server() -> None:
    parser = argparse.ArgumentParser(
        description="MCP server for mastodon_peaker_score select/update tools"
    )
    parser.add_argument(
        "--transport",
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
        help="stdio or http (http maps to streamable-http)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_HOST", "127.0.0.1"),
        help="HTTP bind host when transport is http",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MCP_PORT", "8000")),
        help="HTTP bind port when transport is http",
    )

    args = parser.parse_args()
    transport = _normalize_transport(args.transport)

    if transport == "stdio":
        mcp.run(transport="stdio")
        return

    mcp.run(transport=transport, host=args.host, port=args.port)


@mcp.tool(name="select_peaker_score")
def select_peaker_score(
    id: int | None = None,
    case_notation: str | None = None,
    crate_name: str | None = None,
    task: str | None = None,
    freq_hz: int | None = None,
    min_freq_hz: int | None = None,
    max_freq_hz: int | None = None,
    sort_by: str = "id_desc",
    limit: int = DEFAULT_LIMIT,
) -> dict[str, Any]:
    """Select rows from mastodon_peaker_score with optional filters."""
    if limit < 1:
        raise ValueError("limit must be >= 1")

    if limit > MAX_LIMIT:
        limit = MAX_LIMIT

    clauses: list[str] = []
    params: dict[str, Any] = {}

    if id is not None:
        clauses.append("id = :id")
        params["id"] = id

    if case_notation:
        clauses.append("case_notation = :case_notation")
        params["case_notation"] = case_notation.strip()

    if crate_name:
        clauses.append("crate_name = :crate_name")
        params["crate_name"] = crate_name.strip()

    if task:
        clauses.append("task = :task")
        params["task"] = task.strip()

    if freq_hz is not None:
        clauses.append("freq_hz = :freq_hz")
        params["freq_hz"] = freq_hz

    if min_freq_hz is not None:
        clauses.append("freq_hz >= :min_freq_hz")
        params["min_freq_hz"] = min_freq_hz

    if max_freq_hz is not None:
        clauses.append("freq_hz <= :max_freq_hz")
        params["max_freq_hz"] = max_freq_hz

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    order_by = _normalize_sort_by(sort_by)
    params["limit"] = limit

    query = text(
        f"""
        SELECT id, case_notation, crate_name, freq_hz, peaker_quantity, service, task
        FROM mastodon_peaker_score
        {where}
        ORDER BY {order_by}
        LIMIT :limit
        """
    )

    with _engine().begin() as conn:
        records = conn.execute(query, params).fetchall()

    rows = [asdict(_row_to_model(row)) for row in records]
    return {
        "row_count": len(rows),
        "rows": rows,
    }


@mcp.tool(name="update_peaker_score")
def update_peaker_score(
    id: int,
    case_notation: str | None = None,
    crate_name: str | None = None,
    freq_hz: int | None = None,
    peaker_quantity: int | None = None,
    service: str | None = None,
    task: str | None = None,
) -> dict[str, Any]:
    """Update one mastodon_peaker_score row by primary key id."""
    if id < 1:
        raise ValueError("id must be >= 1")

    updates: list[str] = []
    params: dict[str, Any] = {"id": id}

    if case_notation is not None:
        case_notation = case_notation.strip()
        if not case_notation:
            raise ValueError("case_notation cannot be empty")
        updates.append("case_notation = :case_notation")
        params["case_notation"] = case_notation

    if crate_name is not None:
        crate_name = crate_name.strip()
        if not crate_name:
            raise ValueError("crate_name cannot be empty")
        updates.append("crate_name = :crate_name")
        params["crate_name"] = crate_name

    if freq_hz is not None:
        updates.append("freq_hz = :freq_hz")
        params["freq_hz"] = freq_hz

    if peaker_quantity is not None:
        if peaker_quantity < 0:
            raise ValueError("peaker_quantity cannot be negative")
        updates.append("peaker_quantity = :peaker_quantity")
        params["peaker_quantity"] = peaker_quantity

    if service is not None:
        service = service.strip()
        if not service:
            raise ValueError("service cannot be empty")
        updates.append("service = :service")
        params["service"] = service

    if task is not None:
        task = task.strip()
        if not task:
            raise ValueError("task cannot be empty")
        updates.append("task = :task")
        params["task"] = task

    if not updates:
        raise ValueError("at least one column must be provided to update")

    with _engine().begin() as conn:
        current = conn.execute(
            text(
                """
                SELECT id, case_notation, crate_name, freq_hz, peaker_quantity, service, task
                FROM mastodon_peaker_score
                WHERE id = :id
                """
            ),
            {"id": id},
        ).fetchone()

        if current is None:
            raise ValueError(f"row not found for id={id}")

        conn.execute(
            text(
                f"""
                UPDATE mastodon_peaker_score
                SET {', '.join(updates)}
                WHERE id = :id
                """
            ),
            params,
        )

        updated = conn.execute(
            text(
                """
                SELECT id, case_notation, crate_name, freq_hz, peaker_quantity, service, task
                FROM mastodon_peaker_score
                WHERE id = :id
                """
            ),
            {"id": id},
        ).fetchone()

    return {
        "before": asdict(_row_to_model(current)),
        "after": asdict(_row_to_model(updated)),
    }


if __name__ == "__main__":
    _run_server()
