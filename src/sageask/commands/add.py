"""Add command — insert a new entity into the bank."""

import sys
from sageask import db


def run(subcommand, part=None, name=None, course_name=None, topic_name=None,
        question=None, model_answer=None, max_mark=None, description=None):
    """Add a course, topic, or question to the bank.

    Args:
        subcommand: 'course', 'topic', or 'question'
    """
    conn = db.get_db()
    try:
        if subcommand == "course":
            _add_course(conn, part, name)
        elif subcommand == "topic":
            _add_topic(conn, course_name, name, description)
        elif subcommand == "question":
            _add_question(conn, course_name, topic_name, question, model_answer, max_mark)
        else:
            print(f"error: unknown subcommand '{subcommand}'", file=sys.stderr)
            return 1
    finally:
        conn.close()
    return 0


def _add_course(conn, part, name):
    """Add a new course."""
    part = part.upper()
    if not name:
        print("error: --name is required", file=sys.stderr)
        return 1
    cid = db.insert_course(conn, part, name)
    print(f"Added course '{name}' ({part}) — id {cid}")
    return 0


def _add_topic(conn, course_name, name, description):
    """Add a new topic to a course."""
    if not course_name or not name:
        print("error: --course_name and --name are required", file=sys.stderr)
        return 1
    cid = db.get_course_id_by_name(conn, course_name)
    if cid is None:
        print(f"error: course '{course_name}' not found — add it first", file=sys.stderr)
        return 1
    tid = db.insert_topic(conn, cid, name, description)
    desc = f" — {description}" if description else ""
    print(f"Added topic '{name}' to '{course_name}' — id {tid}{desc}")
    return 0


def _add_question(conn, course_name, topic_name, question, model_answer, max_mark):
    """Add a new question to a topic."""
    if not course_name or not topic_name or not question or max_mark is None:
        print("error: --course_name, --topic_name, --question, --max_mark are required", file=sys.stderr)
        return 1
    cid = db.get_course_id_by_name(conn, course_name)
    if cid is None:
        print(f"error: course '{course_name}' not found — add it first", file=sys.stderr)
        return 1
    tid = db.get_topic_id_by_name_and_course(conn, course_name, topic_name)
    if tid is None:
        print(f"error: topic '{topic_name}' not found in course '{course_name}' — add it first", file=sys.stderr)
        return 1
    qid = db.insert_question(conn, question, model_answer, max_mark, tid)
    print(f"Added question {qid} to {topic_name} ({course_name})")
    return 0
