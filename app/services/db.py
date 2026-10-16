import json
import os

import pymysql

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    rules VARCHAR(255) NOT NULL,
    evidence TEXT NOT NULL,
    report JSON NOT NULL
)
"""


def db_enabled():
    """The database is used only when MYSQL_HOST is set."""
    return bool(os.environ.get("MYSQL_HOST"))


def _connect():
    conn = pymysql.connect(
        host=os.environ["MYSQL_HOST"],
        user=os.environ.get("MYSQL_USER", ""),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", ""),
        connect_timeout=3,
        cursorclass=pymysql.cursors.DictCursor,
    )
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE)
    return conn


def save_incident(report):
    """Save a diagnosis report. Returns the incident ID, or None if not saved."""
    if not db_enabled():
        return None
    try:
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO incidents (rules, evidence, report) VALUES (%s, %s, %s)",
                    (
                        ",".join(f["rule"] for f in report["findings"]),
                        report["evidence"],
                        json.dumps(report),
                    ),
                )
                incident_id = cur.lastrowid
            conn.commit()
            return incident_id
        finally:
            conn.close()
    except pymysql.MySQLError:
        return None


def list_incidents(limit=50):
    """Return recent incidents, newest first."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, created_at, status, rules, evidence "
                "FROM incidents ORDER BY id DESC LIMIT %s",
                (limit,),
            )
            return cur.fetchall()
    finally:
        conn.close()
