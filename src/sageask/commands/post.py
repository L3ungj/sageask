"""Post command — post next unanswered (or specified) question."""

import sys

from sageask import db, config, discord


def run(question_text, answer_text, question_id, course_id, max_mark, topic_name):
    """Post a question to Discord."""
    # Inline insert mode: --question + --answer + --course + --max_mark
    if question_text is not None:
        if not answer_text:
            print("error: --answer is required with --question", file=sys.stderr)
            return 1
        if not course_id:
            print("error: --course is required for insert mode", file=sys.stderr)
            return 1
        conn = db.get_db()
        try:
            cid = db.get_course_id_by_name(conn, course_id)
            if cid is None:
                print(f"error: course '{course_id}' not found", file=sys.stderr)
                return 1
            tid = None
            if topic_name:
                tid = db.get_topic_id_by_name_and_course(conn, course_id, topic_name)
                if tid is None:
                    print(f"error: topic '{topic_name}' not found in course '{course_id}'", file=sys.stderr)
                    return 1
            else:
                # Create or get a default topic for this course
                tid = db.get_topic_id_by_name_and_course(conn, course_id, "General")
                if tid is None:
                    tid = db.insert_topic(conn, cid, "General")
            qid = db.insert_question(conn, question_text, answer_text, max_mark, tid)
        finally:
            conn.close()
        question_id = qid

    conn = db.get_db()
    try:
        if db.has_unanswered_posted_question(conn):
            print("A question is already posted and awaiting a reply.", file=sys.stderr)
            return 1

        if question_id:
            q = db.get_question_by_id(conn, question_id)
        else:
            q = db.get_next_question_srs(conn)

        if q is None:
            print("No unanswered question found.", file=sys.stderr)
            return 1

        msg_id = discord.post_message(
            config.DISCORD_HOME_CHANNEL,
            f"[({q['course_part']}) {q['course_name']} ({q['topic_name']})] {q['question']} [{q['max_mark']} marks]",
        )

        # Create thread under the message (thread channel ID equals message ID for public threads)
        thread_name = f"[({q['course_part']}) {q['course_name']}] {q['question'][:50]}"
        discord.create_thread(
            config.DISCORD_HOME_CHANNEL,
            msg_id,
            name=thread_name,
        )

        db.mark_posted(conn, q["id"], msg_id)
        print(f"Question ID: {q['id']}")
        print(f"Discord message ID: {msg_id}")
    finally:
        conn.close()

    return 0
