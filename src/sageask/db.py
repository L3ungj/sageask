"""SQLite question bank for SageAsk."""

import sqlite3
import os
from datetime import datetime, timezone

from sageask import config


def _resolve_db_path():
    return os.path.join(config._DATA_DIR, "questions.db")


CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS courses (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    part    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS topics (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id   INTEGER NOT NULL REFERENCES courses(id),
    name        TEXT NOT NULL,
    description TEXT,
    UNIQUE(course_id, name)
);

CREATE TABLE IF NOT EXISTS questions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id        INTEGER REFERENCES topics(id),
    question        TEXT NOT NULL,
    model_answer    TEXT,
    max_mark        INTEGER NOT NULL DEFAULT 1,
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


# ── Courses ──────────────────────────────────────────────────────────

def get_courses(conn, course_name=None):
    """Return all courses as list of dicts."""
    base_sql = "SELECT id, name, part FROM courses"
    params = []
    if course_name:
        base_sql += " WHERE name = ?"
        params.append(course_name)
    base_sql += " ORDER BY part, name"

    cur = conn.execute(base_sql, params)
    rows = cur.fetchall()
    return [{"id": r[0], "name": r[1], "part": r[2]} for r in rows]


def get_course(conn, course_id):
    """Return a single course as dict, or None."""
    cur = conn.execute("SELECT id, name, part FROM courses WHERE id = ?", (course_id,))
    row = cur.fetchone()
    if row is None:
        return None
    return {"id": row[0], "name": row[1], "part": row[2]}


def get_course_id_by_name(conn, course_name):
    """Return course id for a course name (by name only)."""
    cur = conn.execute("SELECT id FROM courses WHERE name = ?", (course_name,))
    row = cur.fetchone()
    return row[0] if row else None


def insert_course(conn, part, name):
    """Insert a course. Returns the id (creates if not exists with this part)."""
    cur = conn.execute("SELECT id FROM courses WHERE name = ? AND part = ?", (name, part))
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute("INSERT INTO courses (name, part) VALUES (?, ?)", (name, part))
    conn.commit()
    return cur.lastrowid


# ── Topics ───────────────────────────────────────────────────────────

def get_topics(conn):
    """Return all topics with course info as list of dicts."""
    cur = conn.execute(
        "SELECT t.id, t.name, t.description, c.name AS course_name, c.part "
        "FROM topics t JOIN courses c ON t.course_id = c.id ORDER BY c.part, c.name, t.name"
    )
    return [{
        "id": r[0], "name": r[1], "description": r[2], "course_name": r[3],
        "course_part": r[4],
    } for r in cur.fetchall()]


def get_topics_by_course(conn, course_name=None, topic_name=None):
    """Return topics filtered by course name (optional).

    Returns list of dicts with id, name, description, course_name, course_part.
    """
    base_sql = (
        "SELECT t.id, t.name, t.description, c.name AS course_name, c.part "
        "FROM topics t JOIN courses c ON t.course_id = c.id"
    )
    params = []
    if course_name:
        base_sql += " WHERE c.name = ?"
        params.append(course_name)
    base_sql += " ORDER BY c.part, c.name, t.name"

    cur = conn.execute(base_sql, params)
    return [{
        "id": r[0], "name": r[1], "description": r[2], "course_name": r[3],
        "course_part": r[4],
    } for r in cur.fetchall() if topic_name is None or r[1] == topic_name]


def get_topic(conn, topic_id):
    """Return a single topic as dict, or None."""
    cur = conn.execute(
        "SELECT t.id, t.name, t.description, c.name, c.part "
        "FROM topics t JOIN courses c ON t.course_id = c.id WHERE t.id = ?",
        (topic_id,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {"id": row[0], "name": row[1], "description": row[2],
            "course_name": row[3], "course_part": row[4]}


def get_topic_id_by_name_and_course(conn, course_name, topic_name):
    """Return topic id by (course_name, topic_name), or None."""
    cur = conn.execute(
        "SELECT t.id FROM topics t JOIN courses c ON t.course_id = c.id "
        "WHERE c.name = ? AND t.name = ?",
        (course_name, topic_name),
    )
    row = cur.fetchone()
    return row[0] if row else None


def insert_topic(conn, course_id, name, description=None):
    """Insert a topic. Returns the id."""
    cur = conn.execute(
        "INSERT INTO topics (course_id, name, description) VALUES (?, ?, ?)",
        (course_id, name, description),
    )
    conn.commit()
    return cur.lastrowid


# ── Questions ────────────────────────────────────────────────────────

def insert_question(conn, question, model_answer, max_mark, topic_id):
    """Insert a new question. Returns the new id."""
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    cur = conn.execute(
        "INSERT INTO questions (topic_id, question, model_answer, max_mark, discord_id, reply_content, reply_timestamp, mark, comment, created_at) "
        "VALUES (?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, ?)",
        (topic_id, question, model_answer, max_mark, now),
    )
    conn.commit()
    return cur.lastrowid


def get_question_by_id(conn, qid):
    """Return a single question as dict, or None."""
    cur = conn.execute(
        "SELECT q.id, q.question, q.model_answer, q.max_mark, q.discord_id, "
        "q.reply_content, q.reply_timestamp, q.mark, q.comment, q.created_at, "
        "t.name AS topic_name, c.name AS course_name, c.part AS course_part "
        "FROM questions q JOIN topics t ON q.topic_id = t.id JOIN courses c ON t.course_id = c.id "
        "WHERE q.id = ?",
        (qid,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "id": row[0], "question": row[1], "model_answer": row[2], "max_mark": row[3],
        "discord_id": row[4], "reply_content": row[5], "reply_timestamp": row[6],
        "mark": row[7], "comment": row[8], "created_at": row[9],
        "topic_name": row[10], "course_name": row[11], "course_part": row[12],
    }


def get_next_question(conn):
    """Return the next unanswered question using SRS urgency.

    Priority:
    1. First unposted question (discord_id IS NULL)
    2. First posted question without a reply
    """
    # Unposted questions
    cur = conn.execute(
        "SELECT q.id, q.question, q.model_answer, q.max_mark, q.discord_id, "
        "t.name AS topic_name, c.name AS course_name, c.part AS course_part "
        "FROM questions q JOIN topics t ON q.topic_id = t.id JOIN courses c ON t.course_id = c.id "
        "WHERE q.discord_id IS NULL "
        "ORDER BY q.id ASC LIMIT 1",
    )
    row = cur.fetchone()
    if row:
        return {
            "id": row[0], "question": row[1], "model_answer": row[2], "max_mark": row[3],
            "discord_id": row[4], "topic_name": row[5],
            "course_name": row[6], "course_part": row[7],
        }

    # Posted but no reply
    cur = conn.execute(
        "SELECT q.id, q.question, q.model_answer, q.max_mark, q.discord_id, "
        "t.name AS topic_name, c.name AS course_name, c.part AS course_part "
        "FROM questions q JOIN topics t ON q.topic_id = t.id JOIN courses c ON t.course_id = c.id "
        "WHERE q.discord_id IS NOT NULL AND q.reply_content IS NULL "
        "ORDER BY q.id ASC LIMIT 1",
    )
    row = cur.fetchone()
    if row:
        return {
            "id": row[0], "question": row[1], "model_answer": row[2], "max_mark": row[3],
            "discord_id": row[4], "topic_name": row[5],
            "course_name": row[6], "course_part": row[7],
        }
    return None


def has_unanswered_posted_question(conn):
    """Return True if there is a posted question with no reply yet."""
    row = conn.execute(
        "SELECT 1 FROM questions "
        "WHERE discord_id IS NOT NULL AND reply_content IS NULL "
        "LIMIT 1"
    ).fetchone()
    return row is not None


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


def get_question_and_answer(conn, qid):
    """Return both question text and model answer for a question, or None."""
    cur = conn.execute("SELECT question, model_answer FROM questions WHERE id = ?", (qid,))
    row = cur.fetchone()
    return (row[0], row[1]) if row else None


def get_question_by_discord_id(conn, discord_id):
    """Look up a question by its Discord message ID."""
    cur = conn.execute(
        "SELECT q.id, q.question, q.model_answer, q.max_mark, q.discord_id, q.reply_content, "
        "q.reply_timestamp, q.mark, q.comment, q.created_at, "
        "t.name AS topic_name, c.name AS course_name, c.part AS course_part "
        "FROM questions q JOIN topics t ON q.topic_id = t.id JOIN courses c ON t.course_id = c.id "
        "WHERE q.discord_id = ?",
        (discord_id,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "id": row[0], "question": row[1], "model_answer": row[2], "max_mark": row[3],
        "discord_id": row[4], "reply_content": row[5], "reply_timestamp": row[6],
        "mark": row[7], "comment": row[8], "created_at": row[9],
        "topic_name": row[10], "course_name": row[11], "course_part": row[12],
    }


def get_latest_posted_question(conn):
    """Return the most recently posted question as dict, or None."""
    cur = conn.execute(
        "SELECT q.id, q.question, q.model_answer, q.max_mark, q.discord_id, "
        "q.reply_content, q.reply_timestamp, q.mark, q.comment, q.created_at, "
        "t.name AS topic_name, c.name AS course_name, c.part AS course_part "
        "FROM questions q JOIN topics t ON q.topic_id = t.id JOIN courses c ON t.course_id = c.id "
        "WHERE q.discord_id IS NOT NULL "
        "ORDER BY q.id DESC LIMIT 1",
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "id": row[0], "question": row[1], "model_answer": row[2], "max_mark": row[3],
        "discord_id": row[4], "reply_content": row[5], "reply_timestamp": row[6],
        "mark": row[7], "comment": row[8], "created_at": row[9],
        "topic_name": row[10], "course_name": row[11], "course_part": row[12],
    }


# ── Question Listing ─────────────────────────────────────────────────

def get_questions(conn, course_name=None, topic_name=None):
    """Return questions with topic/course info, optionally filtered.

    Args:
        course_name: Filter by course name (optional)
        topic_name: Filter by topic name (requires course_name)

    Returns list of dicts with id, question, topic_name, course_name, etc.
    """
    base_sql = (
        "SELECT q.id, q.question, q.max_mark, q.mark, q.comment, "
        "t.name AS topic_name, c.name AS course_name, c.part AS course_part "
        "FROM questions q JOIN topics t ON q.topic_id = t.id JOIN courses c ON t.course_id = c.id"
    )
    conditions = []
    params = []
    if course_name:
        conditions.append("c.name = ?")
        params.append(course_name)
    if topic_name:
        conditions.append("t.name = ?")
        params.append(topic_name)

    if conditions:
        base_sql += " WHERE " + " AND ".join(conditions)
    base_sql += " ORDER BY c.part, c.name, t.name, q.id"

    cur = conn.execute(base_sql, params)
    return [{
        "id": r[0], "question": r[1], "max_mark": r[2], "mark": r[3],
        "comment": r[4], "topic_name": r[5], "course_name": r[6],
        "course_part": r[7],
    } for r in cur.fetchall()]


# ── Summary & SRS ────────────────────────────────────────────────────

def get_topic_topic_summary(conn):
    """Return per-topic unanswered counts and basic info.

    Returns list of dicts: id, name, course_name, course_part, unanswered, total
    """
    cur = conn.execute(
        "SELECT t.id, t.name, c.name AS course_name, c.part AS course_part, "
        "SUM(CASE WHEN q.mark IS NULL AND q.id IS NOT NULL THEN 1 ELSE 0 END) AS unanswered, "
        "COUNT(q.id) AS total "
        "FROM topics t JOIN courses c ON t.course_id = c.id "
        "LEFT JOIN questions q ON q.topic_id = t.id "
        "GROUP BY t.id "
        "ORDER BY c.part, c.name, t.name"
    )
    return [{
        "id": r[0], "name": r[1], "course_name": r[2], "course_part": r[3],
        "unanswered": r[4], "total": r[5],
    } for r in cur.fetchall()]


def compute_topic_score(conn, topic_id):
    """Compute SRS score for a topic.

    For each graded question:
        days = (now - reply_timestamp) / 86400
        decay = 0.995 ** days
        individual_score = (mark / max_mark) * decay

    score = mean(individual_scores) across graded questions
    For ungraded topics: score = 0

    Returns (score, list of (days, mark/max_mark) tuples for display).
    """
    cur = conn.execute(
        "SELECT mark, max_mark, reply_timestamp FROM questions "
        "WHERE topic_id = ? AND mark IS NOT NULL "
        "ORDER BY reply_timestamp DESC",
        (topic_id,),
    )
    rows = cur.fetchall()

    if not rows:
        return (0, [])

    scores = []
    for mark, max_mark, ts in rows:
        days = 0
        if ts:
            days = (datetime.now(timezone.utc) - datetime.fromisoformat(ts)).total_seconds() / 86400
        decay = 0.995 ** days
        scores.append(((mark / max_mark) * decay, days, mark / max_mark))

    score = sum(s[0] for s in scores) / len(scores)
    return (score, scores)


def get_next_question_srs(conn):
    """Return the next question using SRS score-based topic selection.

    Picks the topic with lowest score (worst performance + stalest review),
    then returns the first unanswered question of that topic.
    """
    topics = get_topic_topic_summary(conn)
    if not topics:
        return None

    best = None
    best_score = float("inf")

    for topic in topics:
        score, scores = compute_topic_score(conn, topic["id"])

        last_score = max((s[0] for s in scores), default=score)
        last_days = max((s[1] for s in scores), default=0)

        t_info = {
            "score": score,
            "last_score": last_score,
            "days_since": round(last_days, 1),
            "unanswered": topic["unanswered"],
        }

        if score < best_score:
            best_score = score
            best = (topic, t_info)

    if best is None:
        return None

    topic_data, t_info = best

    cur = conn.execute(
        "SELECT q.id, q.question, q.model_answer, q.max_mark, q.discord_id, "
        "t.name AS topic_name, c.name AS course_name, c.part AS course_part "
        "FROM questions q JOIN topics t ON q.topic_id = t.id JOIN courses c ON t.course_id = c.id "
        "WHERE q.topic_id = ? AND (q.discord_id IS NULL OR q.reply_content IS NULL) "
        "ORDER BY q.id ASC LIMIT 1",
        (topic_data["id"],),
    )
    row = cur.fetchone()
    if row is None:
        return None

    return {
        "id": row[0], "question": row[1], "model_answer": row[2], "max_mark": row[3],
        "discord_id": row[4], "topic_name": row[5],
        "course_name": row[6], "course_part": row[7],
        "topic_info": t_info,
    }


def get_summary(conn):
    """Return a summary dict with counts and SRS data."""
    total = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]

    unanswered = conn.execute(
        "SELECT COUNT(*) FROM questions WHERE mark IS NULL"
    ).fetchone()[0]

    graded = conn.execute(
        "SELECT COUNT(*) FROM questions WHERE mark IS NOT NULL"
    ).fetchone()[0]

    # Topic scoring data
    topics = get_topic_topic_summary(conn)
    tight_topics = []
    weak_topics = []
    if topics:
        for t in topics:
            # Tight: 2 or fewer unanswered questions
            if t["unanswered"] <= 2:
                tight_topics.append({
                    "course_name": t["course_name"],
                    "topic_name": t["name"],
                    "unanswered": t["unanswered"],
                })

            score, scores = compute_topic_score(conn, t["id"])
            last_score = max((s[0] for s in scores), default=score)
            last_days = max((s[1] for s in scores), default=0)

            weak_topics.append({
                "course_name": t["course_name"],
                "topic_name": t["name"],
                "score": score,
                "last_score": last_score,
                "days_since": round(last_days, 1),
            })

        tight_topics.sort(key=lambda x: x["unanswered"])
        weak_topics.sort(key=lambda x: x["score"])

    # Next question via SRS
    next_q = get_next_question_srs(conn)

    return {
        "total": total,
        "unanswered": unanswered,
        "graded": graded,
        "tight_topics": tight_topics,
        "weak_topics": weak_topics,
        "next_question": next_q,
    }
