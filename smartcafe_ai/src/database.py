import datetime
import logging
import os
import sqlite3
from typing import Dict, List, Optional

import pandas as pd

ITEMS = ["cafe_hat", "cafe_xay", "ly_giay", "ly_nhua", "sua_dac"]
logger = logging.getLogger(__name__)


def _base_dir() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _data_dir() -> str:
    path = os.path.join(_base_dir(), "data")
    os.makedirs(path, exist_ok=True)
    return path


def _db_path() -> str:
    default_path = os.path.join(_data_dir(), "db", "smartcafe.db")
    path = os.getenv("SMARTCAFE_DB_PATH", default_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def _csv_path() -> str:
    return os.path.join(_data_dir(), "inventory.csv")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recorded_at TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'ai',
                cafe_hat INTEGER NOT NULL DEFAULT 0,
                cafe_xay INTEGER NOT NULL DEFAULT 0,
                ly_giay INTEGER NOT NULL DEFAULT 0,
                ly_nhua INTEGER NOT NULL DEFAULT 0,
                sua_dac INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                changed_at TEXT NOT NULL,
                actor TEXT NOT NULL,
                field TEXT NOT NULL,
                old_value INTEGER NOT NULL,
                new_value INTEGER NOT NULL,
                reason TEXT,
                context TEXT
            )
            """
        )
    migrate_csv_to_sqlite()


def migrate_csv_to_sqlite() -> None:
    csv_file = _csv_path()
    if not os.path.exists(csv_file):
        return

    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM inventory_snapshots").fetchone()["c"]
        if total > 0:
            return

    try:
        df = pd.read_csv(csv_file)
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as ex:
        logger.warning("CSV migration skipped because CSV could not be read: %s", ex)
        return

    if df.empty:
        return

    records: List[Dict[str, int]] = []
    for _, row in df.iterrows():
        records.append(
            {
                "recorded_at": str(row.get("Thời gian", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                **{item: int(row.get(item, 0) or 0) for item in ITEMS},
            }
        )

    with _connect() as conn:
        conn.executemany(
            """
            INSERT INTO inventory_snapshots
            (recorded_at, source, cafe_hat, cafe_xay, ly_giay, ly_nhua, sua_dac)
            VALUES (:recorded_at, 'csv_migration', :cafe_hat, :cafe_xay, :ly_giay, :ly_nhua, :sua_dac)
            """,
            records,
        )


def get_latest_inventory() -> Dict[str, int]:
    init_database()
    with _connect() as conn:
        row = conn.execute(
            "SELECT cafe_hat, cafe_xay, ly_giay, ly_nhua, sua_dac "
            "FROM inventory_snapshots ORDER BY id DESC LIMIT 1"
        ).fetchone()

    if not row:
        return {item: 0 for item in ITEMS}
    return {item: int(row[item]) for item in ITEMS}


def save_inventory(
    inventory_counts: Dict[str, int],
    source: str = "ai",
    actor: str = "system",
    previous_counts: Optional[Dict[str, int]] = None,
    reason: Optional[str] = None,
) -> bool:
    init_database()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {item: int(inventory_counts.get(item, 0) or 0) for item in ITEMS}

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO inventory_snapshots
            (recorded_at, source, cafe_hat, cafe_xay, ly_giay, ly_nhua, sua_dac)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now,
                source,
                payload["cafe_hat"],
                payload["cafe_xay"],
                payload["ly_giay"],
                payload["ly_nhua"],
                payload["sua_dac"],
            ),
        )

        if previous_counts is not None:
            audit_rows = []
            for item in ITEMS:
                old_value = int(previous_counts.get(item, 0) or 0)
                new_value = payload[item]
                if old_value != new_value:
                    audit_rows.append((now, actor, item, old_value, new_value, reason, source))
            if audit_rows:
                conn.executemany(
                    """
                    INSERT INTO inventory_audit_log
                    (changed_at, actor, field, old_value, new_value, reason, context)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    audit_rows,
                )

    _save_inventory_to_csv(payload, now)
    return True


def _save_inventory_to_csv(inventory_counts: Dict[str, int], now: str) -> None:
    csv_file_path = _csv_path()
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Thời gian"] + ITEMS)

    new_row = {"Thời gian": now}
    for item in ITEMS:
        new_row[item] = int(inventory_counts.get(item, 0) or 0)

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")


def save_inventory_to_csv(inventory_counts: Dict[str, int], actor: str = "staff", reason: str = "manual_adjustment") -> bool:
    previous = get_latest_inventory()
    return save_inventory(
        inventory_counts=inventory_counts,
        source="manual",
        actor=actor,
        previous_counts=previous,
        reason=reason,
    )


def get_inventory_history(limit: int = 200) -> pd.DataFrame:
    init_database()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT recorded_at AS "Thời gian", cafe_hat, cafe_xay, ly_giay, ly_nhua, sua_dac
            FROM inventory_snapshots
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(row) for row in rows])


def get_audit_log(limit: int = 200) -> pd.DataFrame:
    init_database()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT changed_at AS "Thời gian", actor AS "Người sửa", field AS "Mặt hàng",
                   old_value AS "Giá trị cũ", new_value AS "Giá trị mới",
                   reason AS "Lý do", context AS "Nguồn"
            FROM inventory_audit_log
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(row) for row in rows])
