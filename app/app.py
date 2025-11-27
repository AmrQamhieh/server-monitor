from datetime import datetime, timedelta
import os

from flask import Flask, jsonify, render_template, request
import mysql.connector

from app.logging_utils import get_logger, log_action

app = Flask(__name__)

logger = get_logger(__name__)


# ------------------- DB helpers (pure MySQL/MariaDB) -------------------


def get_db_connection():
    """
    Open a new connection to the MariaDB/MySQL database using env vars.
    """
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "monitor"),
        password=os.getenv("DB_PASSWORD", "monitorpass"),
        database=os.getenv("DB_NAME", "usage_db"),  # <- matches your MariaDB DB
    )
    return conn


def fetch_one(query, params=None):
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        row = cur.fetchone()
        return row
    finally:
        cur.close()
        conn.close()


def fetch_all(query, params=None):
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()


# ------------------- Shared query helpers -------------------


def get_latest_row():
    """
    Return the most recent row from usage_stats table.
    """
    sql = """
        SELECT id, cpu, mem, disk, ts
        FROM usage_stats
        ORDER BY ts DESC
        LIMIT 1
    """
    return fetch_one(sql)


def get_rows_last_24h():
    """
    Return all rows from last 24 hours (ordered ascending by time).
    """
    since = datetime.utcnow() - timedelta(hours=24)
    sql = """
        SELECT id, cpu, mem, disk, ts
        FROM usage_stats
        WHERE ts >= %s
        ORDER BY ts ASC
    """
    return fetch_all(sql, (since,))


def normalize_timestamp(ts):
    if isinstance(ts, datetime):
        return ts.isoformat()
    if ts is None:
        return None
    # fallback
    return str(ts)


def usage_to_dict(row: dict) -> dict:
    """
    Normalize row dict to JSON-friendly dict.
    """
    if row is None:
        return None
    return {
        "id": row.get("id"),
        "cpu": row.get("cpu"),
        "mem": row.get("mem"),
        "disk": row.get("disk"),
        # keep JSON key name "timestamp", but read DB column "ts"
        "timestamp": normalize_timestamp(row.get("ts")),
    }


# ------------------- API endpoints -------------------


@app.route("/health")
@log_action
def health():
    logger.info(f"/health called from {request.remote_addr}")
    return jsonify({"status": "ok"})


# ----- general combined endpoints -----


@app.route("/latest")
@log_action
def latest():
    row = get_latest_row()
    if row is None:
        return jsonify({"message": "no data yet"}), 404
    return jsonify(usage_to_dict(row))


@app.route("/last24hours")
@log_action
def last_24_hours():
    rows = get_rows_last_24h()
    data = [usage_to_dict(r) for r in rows]
    return jsonify(data)


# ----- CPU-specific -----


@app.route("/cpu/current")
@log_action
def cpu_current():
    row = get_latest_row()
    if row is None:
        return jsonify({"message": "no data yet"}), 404

    return jsonify(
        {
            "cpu": row.get("cpu"),
            "timestamp": normalize_timestamp(row.get("ts")),
        }
    )


@app.route("/cpu/last24hours")
@log_action
def cpu_last_24_hours():
    rows = get_rows_last_24h()
    data = [
        {
            "cpu": r.get("cpu"),
            "timestamp": normalize_timestamp(r.get("ts")),
        }
        for r in rows
    ]
    return jsonify(data)


# ----- MEM-specific -----


@app.route("/mem/current")
@log_action
def mem_current():
    row = get_latest_row()
    if row is None:
        return jsonify({"message": "no data yet"}), 404

    return jsonify(
        {
            "mem": row.get("mem"),
            "timestamp": normalize_timestamp(row.get("ts")),
        }
    )


@app.route("/mem/last24hours")
@log_action
def mem_last_24_hours():
    rows = get_rows_last_24h()
    data = [
        {
            "mem": r.get("mem"),
            "timestamp": normalize_timestamp(r.get("ts")),
        }
        for r in rows
    ]
    return jsonify(data)


# ----- DISK-specific -----


@app.route("/disk/current")
@log_action
def disk_current():
    row = get_latest_row()
    if row is None:
        return jsonify({"message": "no data yet"}), 404

    return jsonify(
        {
            "disk": row.get("disk"),
            "timestamp": normalize_timestamp(row.get("ts")),
        }
    )


@app.route("/disk/last24hours")
@log_action
def disk_last_24_hours():
    rows = get_rows_last_24h()
    data = [
        {
            "disk": r.get("disk"),
            "timestamp": normalize_timestamp(r.get("ts")),
        }
        for r in rows
    ]
    return jsonify(data)


# ------------------- Dashboard HTML -------------------


@app.route("/")
@log_action
def dashboard():
    latest_row = get_latest_row()
    last24_rows = get_rows_last_24h()

    # Jinja can access dict keys like attributes: row.cpu, row.mem, etc.
    return render_template(
        "dashboard.html",
        latest=latest_row,
        rows=last24_rows,
    )


if __name__ == "__main__":
    # For local dev
    app.run(host="0.0.0.0", port=5001)

