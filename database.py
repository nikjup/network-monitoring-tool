
import sqlite3

DB_NAME = "network.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_name TEXT,
            ip TEXT,
            issue TEXT,
            severity TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def create_incident(device_name, ip, issue, severity):

    conn = get_connection()
    cursor = conn.cursor()

    # Avoid duplicate active incidents for the same device
    cursor.execute("""
        SELECT id FROM incidents
        WHERE ip = ? AND status IN ('Open', 'Acknowledged')
    """, (ip,))

    existing = cursor.fetchone()

    if not existing:
        cursor.execute("""
            INSERT INTO incidents
            (device_name, ip, issue, severity, status)
            VALUES (?, ?, ?, ?, 'Open')
        """, (device_name, ip, issue, severity))

    conn.commit()
    conn.close()


def get_incidents():

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    incidents = conn.execute("""
        SELECT * FROM incidents
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return incidents


def acknowledge_incident(incident_id):

    conn = get_connection()

    conn.execute("""
        UPDATE incidents
        SET status = 'Acknowledged'
        WHERE id = ? AND status = 'Open'
    """, (incident_id,))

    conn.commit()
    conn.close()


def resolve_incident(ip):

    conn = get_connection()

    conn.execute("""
        UPDATE incidents
        SET status = 'Resolved'
        WHERE ip = ? AND status IN ('Open', 'Acknowledged')
    """, (ip,))

    conn.commit()
    conn.close()
