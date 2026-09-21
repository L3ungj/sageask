"""List command — list courses, topics, and questions."""

from sageask import db


def run(entity, course_name=None, topic_name=None):
    """List courses, topics, or questions with optional filters.

    Args:
        entity: 'courses', 'topics', or 'questions'
        course_name: Filter by course name (optional)
        topic_name: Filter by topic name (optional, requires course_name)
    """
    conn = db.get_db()
    try:
        if entity == "courses":
            _list_courses(conn, course_name)
        elif entity == "topics":
            _list_topics(conn, course_name, topic_name)
        elif entity == "questions":
            _list_questions(conn, course_name, topic_name)
        else:
            print(f"error: unknown entity '{entity}' — use 'courses', 'topics', or 'questions'", file=__import__('sys').stderr)
            return 1
    finally:
        conn.close()
    return 0


def _list_courses(conn, course_name=None):
    courses = db.get_courses(conn, course_name)
    if not courses:
        print("No courses found.")
        return
    print(f"{'ID':<5} {'Part':<5} {'Name'}")
    print("-" * 40)
    for c in courses:
        print(f"{c['id']:<5} {c['part']:<5} {c['name']}")


def _list_topics(conn, course_name=None, topic_name=None):
    topics = db.get_topics_by_course(conn, course_name, topic_name)
    if course_name:
        print(f"Topics for '{course_name}':")
    else:
        print("Topics:")
    print(f"{'ID':<5} {'Part':<5} {'Course':<20} {'Name':<30} Description")
    print("-" * 100)
    for t in topics:
        print(f"{t['id']:<5} {t['course_part']:<5} {t['course_name']:<20} {t['name']:<30} {t['description']}")
    if not topics:
        print("No topics found.")


def _list_questions(conn, course_name=None, topic_name=None):
    questions = db.get_questions(conn, course_name, topic_name)
    if course_name:
        if topic_name:
            print(f"Questions for '{topic_name}' ({course_name}):")
        else:
            print(f"Questions for '{course_name}':")
    else:
        print("Questions:")
    for q in questions:
        mark = f" ({q['mark']}/{q['max_mark']})" if q['mark'] is not None else f"/{q['max_mark']}"
        print(f"  [{q['id']}] ({q['course_name']} — {q['topic_name']}) {q['question']} {mark}")
    if not questions:
        print("No questions found.")
