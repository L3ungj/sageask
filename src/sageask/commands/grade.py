"""Grade command — grade a student's reply in the thread."""

import sys

from sageask import db, config, discord


def run(mark, comment, question_discord_id=None):
    """Grade a question's reply and post the grade in the thread.

    Args:
        mark: Numeric mark
        comment: Grading feedback
        question_discord_id: Optional Discord message ID of the question.
                             If None, uses the most recent posted question.
    """
    conn = db.get_db()
    try:
        if question_discord_id is None:
            q = db.get_latest_posted_question(conn)
            if q is None:
                print("error: no posted questions found", file=sys.stderr)
                return 1
        else:
            q = db.get_question_by_discord_id(conn, question_discord_id)
            if q is None:
                print(f"error: no question found for Discord message ID {question_discord_id}", file=sys.stderr)
                return 1

        if q["reply_content"] is None:
            print("error: no reply to grade — check for replies first", file=sys.stderr)
            return 1

    finally:
        conn.close()

    qid = q["id"]

    conn = db.get_db()
    try:
        db.update_grading(conn, qid, mark, comment)

        grade_message = f"Mark: {mark}\n{comment}"
        discord.post_message(q["discord_id"], grade_message)

        print(f"Graded question {qid}: {mark} — {comment}")
    finally:
        conn.close()

    return 0
