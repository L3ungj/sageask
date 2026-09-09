"""SQLite question bank for SageAsk."""

import sqlite3
import os
from datetime import datetime

from sageask import config


def _resolve_db_path():
    return os.path.join(config._DATA_DIR, "questions.db")


CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS courses (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    part    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id       INTEGER NOT NULL REFERENCES courses(id),
    question        TEXT NOT NULL,
    model_answer    TEXT,
    discord_id      TEXT,
    reply_content   TEXT,
    reply_timestamp TEXT,
    mark            INTEGER,
    comment         TEXT,
    created_at      TEXT NOT NULL
);
"""


def get_db(db_path=None):
    """Open a connection with WAL mode."""
    db_path = db_path or _resolve_db_path()
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(CREATE_SCHEMA)
    conn.commit()
    return conn


def init_db(db_path=None):
    """Ensure tables exist. Call once at startup."""
    conn = get_db(db_path)
    conn.close()


def get_courses(conn):
    """Return all courses as list of dicts."""
    cur = conn.execute("SELECT id, name, part FROM courses ORDER BY part, name")
    rows = cur.fetchall()
    return [{"id": r[0], "name": r[1], "part": r[2]} for r in rows]


def get_course(conn, course_id):
    """Return a single course as dict, or None."""
    cur = conn.execute("SELECT id, name, part FROM courses WHERE id = ?", (course_id,))
    row = cur.fetchone()
    if row is None:
        return None
    return {"id": row[0], "name": row[1], "part": row[2]}


def insert_question(conn, question, model_answer, course_id):
    """Insert a new question. Returns the new id."""
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    cur = conn.execute(
        "INSERT INTO questions (course_id, question, model_answer, discord_id, reply_content, reply_timestamp, mark, comment, created_at) "
        "VALUES (?, ?, ?, NULL, NULL, NULL, NULL, NULL, ?)",
        (course_id, question, model_answer, now),
    )
    conn.commit()
    return cur.lastrowid


def get_question_by_id(conn, qid):
    """Return a single question as dict, or None."""
    cur = conn.execute(
        "SELECT q.id, q.question, q.model_answer, q.discord_id, "
        "q.reply_content, q.reply_timestamp, q.mark, q.comment, q.created_at, "
        "c.name, c.part "
        "FROM questions q JOIN courses c ON q.course_id = c.id "
        "WHERE q.id = ?",
        (qid,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "question": row[1],
        "model_answer": row[2],
        "discord_id": row[3],
        "reply_content": row[4],
        "reply_timestamp": row[5],
        "mark": row[6],
        "comment": row[7],
        "created_at": row[8],
        "course_name": row[9],
        "course_part": row[10],
    }


def get_next_question(conn, course_id=None):
    """Return the next unanswered question as dict.

    Priority:
    1. First unposted question (discord_id IS NULL)
    2. First posted question without a reply (discord_id IS NOT NULL AND reply_content IS NULL)
    """
    if course_id:
        cur = conn.execute(
            "SELECT q.id, q.question, q.model_answer, q.discord_id, c.name, c.part "
            "FROM questions q JOIN courses c ON q.course_id = c.id "
            "WHERE q.discord_id IS NULL AND q.course_id = ? "
            "ORDER BY q.id ASC LIMIT 1",
            (course_id,),
        )
    else:
        cur = conn.execute(
            "SELECT q.id, q.question, q.model_answer, q.discord_id, c.name, c.part "
            "FROM questions q JOIN courses c ON q.course_id = c.id "
            "WHERE q.discord_id IS NULL "
            "ORDER BY q.id ASC LIMIT 1",
        )
    row = cur.fetchone()
    if row:
        return {
            "id": row[0],
            "question": row[1],
            "model_answer": row[2],
            "discord_id": row[3],
            "course_name": row[4],
            "course_part": row[5],
        }

    if course_id:
        cur = conn.execute(
            "SELECT q.id, q.question, q.model_answer, q.discord_id, c.name, c.part "
            "FROM questions q JOIN courses c ON q.course_id = c.id "
            "WHERE q.discord_id IS NOT NULL AND q.reply_content IS NULL AND q.course_id = ? "
            "ORDER BY q.id ASC LIMIT 1",
            (course_id,),
        )
    else:
        cur = conn.execute(
            "SELECT q.id, q.question, q.model_answer, q.discord_id, c.name, c.part "
            "FROM questions q JOIN courses c ON q.course_id = c.id "
            "WHERE q.discord_id IS NOT NULL AND q.reply_content IS NULL "
            "ORDER BY q.id ASC LIMIT 1",
        )
    row = cur.fetchone()
    if row:
        return {
            "id": row[0],
            "question": row[1],
            "model_answer": row[2],
            "discord_id": row[3],
            "course_name": row[4],
            "course_part": row[5],
        }
    return None


def mark_posted(conn, qid, discord_id):
    """Mark a question as posted."""
    conn.execute("UPDATE questions SET discord_id = ? WHERE id = ?", (discord_id, qid))
    conn.commit()


def mark_replied(conn, qid, content, timestamp):
    """Mark a question as replied."""
    conn.execute(
        "UPDATE questions SET reply_content = ?, reply_timestamp = ? WHERE id = ?",
        (content, timestamp, qid),
    )
    conn.commit()


def update_grading(conn, qid, mark, comment):
    """Update grading for a question."""
    conn.execute("UPDATE questions SET mark = ?, comment = ? WHERE id = ?", (mark, comment, qid))
    conn.commit()


def get_answer(conn, qid):
    """Return model_answer for a question, or None."""
    cur = conn.execute("SELECT model_answer FROM questions WHERE id = ?", (qid,))
    row = cur.fetchone()
    return row[0] if row else None


def get_summary(conn, course_id=None):
    """Return a summary dict with counts."""
    where = ""
    params = ()
    if course_id:
        where = "WHERE course_id = ?"
        params = (course_id,)

    total = conn.execute(f"SELECT COUNT(*) FROM questions {where}", params).fetchone()[0]

    if where:
        unanswered = conn.execute(f"SELECT COUNT(*) FROM questions {where} AND (discord_id IS NULL OR reply_content IS NULL)", params).fetchone()[0]
        graded = conn.execute(f"SELECT COUNT(*) FROM questions {where} AND mark IS NOT NULL", params).fetchone()[0]
    else:
        unanswered = conn.execute("SELECT COUNT(*) FROM questions WHERE discord_id IS NULL OR reply_content IS NULL").fetchone()[0]
        graded = conn.execute("SELECT COUNT(*) FROM questions WHERE mark IS NOT NULL").fetchone()[0]
    answered = total - unanswered

    if course_id:
        cur = conn.execute(
            f"SELECT q.id, q.question, c.name, c.part FROM questions q JOIN courses c ON q.course_id = c.id {where} ORDER BY q.id ASC LIMIT 1",
            params,
        )
    else:
        cur = conn.execute(
            f"SELECT q.id, q.question, c.name, c.part FROM questions q JOIN courses c ON q.course_id = c.id {where} AND q.discord_id IS NULL ORDER BY q.id ASC LIMIT 1"
        )
    row = cur.fetchone()
    next_q = None
    if row:
        next_q = {"id": row[0], "question": row[1][:80], "course_name": row[2], "course_part": row[3]}

    course_breakdown = None
    if not course_id:
        cur = conn.execute(
            "SELECT c.id, c.name, c.part, COUNT(q.id), SUM(CASE WHEN q.discord_id IS NULL OR q.reply_content IS NULL THEN 1 ELSE 0 END) "
            "FROM courses c LEFT JOIN questions q ON c.id = q.course_id "
            "GROUP BY c.id ORDER BY c.part, c.name"
        )
        course_breakdown = []
        for row in cur:
            course_breakdown.append({
                "id": row[0],
                "name": row[1],
                "part": row[2],
                "total": row[3],
                "unanswered": row[4],
            })

    return {
        "total": total,
        "unanswered": unanswered,
        "answered": answered,
        "graded": graded,
        "next_question": next_q,
        "course_breakdown": course_breakdown,
    }


def get_question_by_discord_id(conn, discord_id):
    """Look up a question by its Discord message ID."""
    cur = conn.execute(
        "SELECT q.id, q.question, q.model_answer, q.discord_id, q.reply_content, "
        "q.reply_timestamp, q.mark, q.comment, q.created_at, c.name, c.part "
        "FROM questions q JOIN courses c ON q.course_id = c.id "
        "WHERE q.discord_id = ?",
        (discord_id,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "question": row[1],
        "model_answer": row[2],
        "discord_id": row[3],
        "reply_content": row[4],
        "reply_timestamp": row[5],
        "mark": row[6],
        "comment": row[7],
        "created_at": row[8],
        "course_name": row[9],
        "course_part": row[10],
    }


def get_latest_posted_question(conn):
    """Return the most recently posted question as dict, or None."""
    cur = conn.execute(
        "SELECT q.id, q.question, q.model_answer, q.discord_id, "
        "q.reply_content, q.reply_timestamp, q.mark, q.comment, q.created_at, "
        "c.name, c.part "
        "FROM questions q JOIN courses c ON q.course_id = c.id "
        "WHERE q.discord_id IS NOT NULL "
        "ORDER BY q.id DESC LIMIT 1",
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "question": row[1],
        "model_answer": row[2],
        "discord_id": row[3],
        "reply_content": row[4],
        "reply_timestamp": row[5],
        "mark": row[6],
        "comment": row[7],
        "created_at": row[8],
        "course_name": row[9],
        "course_part": row[10],
    }
