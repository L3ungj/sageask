"""Add command — insert a new question into the bank."""

from sageask import db, config


def run(part, course_name, question):
    """Add a new question to the bank.

    Args:
        part: Course part (IA, IB, II, III)
        course_name: Course name
        question: Question text
    """
    conn = db.get_db()
    try:
        cur = conn.execute(
            "SELECT id FROM courses WHERE name = ? AND part = ?",
            (course_name, part),
        )
        row = cur.fetchone()
        if row:
            course_id = row[0]
        else:
            cur = conn.execute(
                "INSERT INTO courses (name, part) VALUES (?, ?)",
                (course_name, part),
            )
            conn.commit()
            course_id = cur.lastrowid

        qid = db.insert_question(conn, question, None, course_id)
        print(f"Added question {qid} to {course_name} ({part})")
    finally:
        conn.close()

    return 0
