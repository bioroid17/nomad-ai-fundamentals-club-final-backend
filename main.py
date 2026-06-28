import os
from datetime import datetime, timedelta

from flask.cli import load_dotenv
import pymysql
from flask import Flask, abort, jsonify, request
from flask_cors import CORS

app = Flask("Focus Timer")
CORS(
    app,
    origins=[
        "http://localhost:5173",
        "https://bioroid17.github.io",
    ],
)

load_dotenv()


def get_db_config():
    return {
        "host": os.getenv("FOCUS_TIMER_DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("FOCUS_TIMER_DB_PORT", 3306)),
        "user": os.getenv("FOCUS_TIMER_DB_USER", "root"),
        "password": os.getenv("FOCUS_TIMER_DB_PASSWORD", ""),
        "db": os.getenv("FOCUS_TIMER_DB_NAME", "focus_timer"),
        "cursorclass": pymysql.cursors.DictCursor,
        "charset": "utf8mb4",
        "autocommit": True,
    }


def get_db_connection():
    return pymysql.connect(**get_db_config())


def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    subject_id INT NOT NULL,
                    duration INT NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)


def row_to_subject(row):
    return {"id": row["id"], "name": row["name"]}


def row_to_session(row):
    return {
        "id": row["id"],
        "subject_id": row["subject_id"],
        "subject_name": row["subject_name"],
        "duration": row["duration"],
        "created_at": row["created_at"].strftime("%Y-%m-%dT%H:%M:%S"),
    }


@app.route("/")
def index():
    return jsonify(
        {
            "name": "Focus Timer Backend",
            "endpoints": [
                "/subjects",
                "/sessions",
                "/stats",
            ],
        }
    )


@app.get("/subjects")
def get_subjects():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM subjects ORDER BY id")
            subjects = [row_to_subject(row) for row in cur.fetchall()]
    return jsonify(subjects)


@app.post("/subjects")
def post_subjects():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "`name` is required"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("INSERT INTO subjects (name) VALUES (%s)", (name,))
                subject_id = cur.lastrowid
            except pymysql.err.IntegrityError:
                return jsonify({"error": "Subject already exists"}), 409
            cur.execute("SELECT id, name FROM subjects WHERE id = %s", (subject_id,))
            subject = row_to_subject(cur.fetchone())
    return jsonify(subject), 201


@app.delete("/subjects/<int:id>")
def delete_subject(id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM subjects WHERE id = %s", (id,))
            if cur.rowcount == 0:
                abort(404)
    return jsonify({"success": True})


@app.get("/sessions")
def get_sessions():
    subject_id = request.args.get("subject_id", type=int)
    date_range = request.args.get("range", "all")
    filters = []
    params = []

    if subject_id is not None:
        filters.append("s.subject_id = %s")
        params.append(subject_id)

    now = datetime.utcnow()
    if date_range == "week":
        start = now - timedelta(days=now.weekday())
        start = datetime(start.year, start.month, start.day)
        filters.append("s.created_at >= %s")
        params.append(start)
    elif date_range == "month":
        start = datetime(now.year, now.month, 1)
        filters.append("s.created_at >= %s")
        params.append(start)

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""
    query = f"""
        SELECT
            s.id,
            s.subject_id,
            sub.name AS subject_name,
            s.duration,
            s.created_at
        FROM sessions s
        JOIN subjects sub ON sub.id = s.subject_id
        {where_clause}
        ORDER BY s.created_at DESC
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
            sessions = [row_to_session(row) for row in cur.fetchall()]
    return jsonify(sessions)


@app.post("/sessions")
def post_sessions():
    data = request.get_json(silent=True) or {}
    subject_id = data.get("subject_id")
    duration = data.get("duration")
    if subject_id is None or duration is None:
        return jsonify({"error": "`subject_id` and `duration` are required"}), 400

    try:
        subject_id = int(subject_id)
        duration = int(duration)
    except (TypeError, ValueError):
        return jsonify({"error": "`subject_id` and `duration` must be integers"}), 400

    if duration <= 0:
        return jsonify({"error": "`duration` must be positive"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM subjects WHERE id = %s", (subject_id,))
            if cur.fetchone() is None:
                abort(404)
            cur.execute(
                "INSERT INTO sessions (subject_id, duration) VALUES (%s, %s)",
                (subject_id, duration),
            )
            session_id = cur.lastrowid
            cur.execute(
                "SELECT s.id, s.subject_id, sub.name AS subject_name, s.duration, s.created_at "
                "FROM sessions s JOIN subjects sub ON sub.id = s.subject_id WHERE s.id = %s",
                (session_id,),
            )
            session = row_to_session(cur.fetchone())
    return jsonify(session), 201


@app.delete("/sessions/<int:id>")
def delete_sessions(id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sessions WHERE id = %s", (id,))
            if cur.rowcount == 0:
                abort(404)
    return jsonify({"success": True})


def get_week_start(dt: datetime):
    start = dt - timedelta(days=dt.weekday())
    return datetime(start.year, start.month, start.day)


def weekday_name(index: int):
    return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][index]


@app.get("/stats")
def stats():
    now = datetime.utcnow()
    week_start = get_week_start(now)
    range_start = week_start
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT SUM(duration) AS total_minutes FROM sessions")
            total_minutes = cur.fetchone()["total_minutes"] or 0

            cur.execute(
                "SELECT COUNT(*) AS session_count FROM sessions WHERE created_at >= %s",
                (range_start,),
            )
            sessions_this_week = cur.fetchone()["session_count"] or 0

            cur.execute(
                "SELECT sub.name AS subject_name, SUM(s.duration) AS minutes "
                "FROM sessions s JOIN subjects sub ON sub.id = s.subject_id "
                "GROUP BY sub.name ORDER BY minutes DESC"
            )
            by_subject = [
                {"name": row["subject_name"], "minutes": int(row["minutes"])}
                for row in cur.fetchall()
            ]

            cur.execute(
                "SELECT WEEKDAY(created_at) AS weekday_index, SUM(duration) AS minutes "
                "FROM sessions WHERE created_at >= %s GROUP BY weekday_index",
                (range_start,),
            )
            weekday_rows = {
                row["weekday_index"]: int(row["minutes"]) for row in cur.fetchall()
            }
            by_weekday = {weekday_name(i): weekday_rows.get(i, 0) for i in range(7)}

            past_month = now - timedelta(days=30)
            cur.execute(
                "SELECT DISTINCT DATE(created_at) AS session_date "
                "FROM sessions WHERE created_at >= %s",
                (past_month,),
            )
            session_dates = {row["session_date"] for row in cur.fetchall()}

    streak = 0
    current = now.date()
    while current in session_dates:
        streak += 1
        current = current - timedelta(days=1)

    return jsonify(
        {
            "streak": streak,
            "total_hours": round(total_minutes / 60, 2),
            "sessions_this_week": sessions_this_week,
            "by_subject": by_subject,
            "by_weekday": by_weekday,
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
