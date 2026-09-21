"""Status command — show question bank summary with SRS scores."""

from sageask import db, config


def run(course_id=None):
    """Display the question bank summary."""
    conn = db.get_db()
    try:
        if course_id:
            course = db.get_course(conn, course_id)
            if course:
                print(f"Course: {course['name']} ({course['part']})")
            print()

        summary = db.get_summary(conn)
        print(f"Total: {summary['total']}")
        print(f"Unanswered: {summary['unanswered']}")
        print(f"Graded: {summary['graded']}")

        # Topics with 2 or fewer unanswered questions
        if summary.get("tight_topics"):
            print()
            print("First 5 topics with 2 or fewer unanswered questions:")
            for t in summary["tight_topics"][:5]:
                print(f"  {t['course_name']} ({t['topic_name']})  "
                      f"— {t['unanswered']} unanswered")

        # Top 5 weakest topics by score (lowest first)
        weak = summary.get("weak_topics", [])
        if weak:
            top5 = weak[:5]
            print()
            print("Top 5 weakest topics:")
            for t in top5:
                print(f"  {t['course_name']} ({t['topic_name']})  "
                      f"score: {t['score']:.2f}  "
                      f"(last: {t['last_score']:.2f}, {t['days_since']}d ago)")

        # Next question via SRS
        if summary.get("next_question"):
            q = summary["next_question"]
            info = q.get("topic_info", {})
            if info:
                print()
                print(f"Next: {q['course_name']} ({q['topic_name']})  "
                      f"[{info['score']:.2f}] — {q['question']}")
            else:
                print()
                print(f"Next: {q['course_name']} ({q['course_part']}) — {q['question']}")
        else:
            print()
            print("WARNING: No questions left!")

        if course_id:
            print()
    finally:
        conn.close()

    return 0
