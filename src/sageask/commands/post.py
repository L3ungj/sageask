"""Post command — post next unanswered (or specified) question."""

import sys

from sageask import db, config, discord


def run(question_text, answer_text, question_id, course_id):
    """Post a question to Discord."""
    if question_text is not None:
        if not answer_text:
            print("error: --answer is required with --question", file=sys.stderr)
            return 1
        if not course_id:
            print("error: --course is required for insert mode", file=sys.stderr)
            return 1
        conn = db.get_db()
        try:
            qid = db.insert_question(conn, question_text, answer_text, course_id)
        finally:
            conn.close()
        question_id = qid

    conn = db.get_db()
    try:
        if question_id:
            q = db.get_question_by_id(conn, question_id)
        else:
            q = db.get_next_question(conn, course_id)

        if q is None:
            print("No unanswered question found.", file=sys.stderr)
            return 1

        msg_id = discord.post_message(
            config.DISCORD_HOME_CHANNEL,
            f"[{q['course_name']} ({q['course_part']})] {q['question']}",
        )

        db.mark_posted(conn, q["id"], msg_id)
        print(f"Question ID: {q['id']}")
        print(f"Discord message ID: {msg_id}")
        print("Create a thread from this message in Discord, then use 'sageask check' to fetch replies.")
    finally:
        conn.close()

    return 0
