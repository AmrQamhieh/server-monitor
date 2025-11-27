import os
import json
import subprocess
import datetime

import mysql.connector
from mysql.connector import Error

from .logging_utils import get_logger  # reuse your logging setup

logger = get_logger(__name__)

# DB config – should match server-monitor.env
DB_HOST = os.getenv("DB_HOST", "usage-db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "server_monitor")
DB_USER = os.getenv("DB_USER", "monitor")
DB_PASSWORD = os.getenv("DB_PASSWORD", "monitorpass")


def get_db_connection():
    """Create a new MariaDB connection."""
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def insert_usage(cpu: float, mem: float, disk: float, ts: datetime.datetime) -> None:
    """Insert one usage row into the 'usage' table."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO usage_stats(cpu, mem, disk, ts)
            VALUES (%s, %s, %s, %s)
            """,
            (cpu, mem, disk, ts),
        )
        conn.commit()
        logger.info("Inserted usage row at %s", ts.isoformat())
    except Error as e:
        logger.error("Error inserting usage row: %s", e)
        raise
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


def main():
    """
    1) Call remote_usage to run the SSH+vmstat/free/df commands on the monitored host
    2) Parse the JSON result
    3) Insert into MariaDB
    """
    logger.info("Running collector_job...")

    # Run the remote_usage script INSIDE the container
    # It should print JSON like: {"cpu": 10.5, "mem": 60.0, "disk": 30.0}
    result_bytes = subprocess.check_output(
        ["python3", "-m", "app.remote_usage"]
    )
    result_str = result_bytes.decode().strip()
    logger.info("remote_usage output: %s", result_str)

    data = json.loads(result_str)

    cpu = float(data["cpu"])
    mem = float(data["mem"])
    disk = float(data["disk"])
    ts = datetime.datetime.utcnow()

    insert_usage(cpu, mem, disk, ts)


if __name__ == "__main__":
    main()

