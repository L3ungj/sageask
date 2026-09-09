"""Status command — show question bank summary."""

from sageask import db, config


def run(course_id=None):
    """Display the question bank summary."""
    conn = db.get_db()
    try:
        summary = db.get_summary(conn, course_id)

        if course_id:
            course = db.get_course(conn, course_id)
            if course:
                print(f"Course: {course['name']} ({course['part']})")
            print()

        print(f"Total: {summary['total']}")
        print(f"Unanswered: {summary['unanswered']}")
        print(f"Answered: {summary['answered']}")
        print(f"Graded: {summary['graded']}")

        if not course_id and summary.get("course_breakdown"):
            print()
            print("Courses:")
            for c in summary["course_breakdown"]:
                print(f"  {c['name']} ({c['part']})   — total: {c['total']}, unanswered: {c['unanswered']}")

        if summary.get("next_question"):
            q = summary["next_question"]
            print()
            print(f"Next: {q['course_name']} ({q['course_part']}) — {q['question']}")

        print()
    finally:
        conn.close()

    return 0
