"""SageAsk CLI — post questions to Discord, check replies."""

import os
import sys

# When run directly (python3 src/sageask/sageask.py), ensure src/ is on sys.path
# so `import sageask` finds the package, not the file itself
_here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _here not in sys.path:
    sys.path.insert(0, _here)

import argparse
from sageask import config, db, discord


def main():
    parser = argparse.ArgumentParser(prog="sageask", description="SageAsk: post questions to Discord, check replies")
    subparsers = parser.add_subparsers(dest="command")

    # status
    status_parser = subparsers.add_parser("status", help="Show question bank status")
    status_parser.add_argument("--course", type=int, help="Filter by course ID")

    # post
    post_parser = subparsers.add_parser("post", help="Post next unanswered (or specified) question")
    post_parser.add_argument("--course", help="Course name (for insert mode)")
    post_parser.add_argument("--question", "-q", help="Question text to post (requires --answer)")
    post_parser.add_argument("--answer", "-a", help="Model answer (requires --question)")
    post_parser.add_argument("--id", type=int, help="Specific question ID to post")
    post_parser.add_argument("--max_mark", type=int, help="Max mark (required with --question)")
    post_parser.add_argument("--topic", help="Topic name (required with --question)")

    # check
    check_parser = subparsers.add_parser("check", help="Check for user's reply")
    check_parser.add_argument("--question", help="Discord message ID of the question (optional, defaults to last posted)")

    # grade
    grade_parser = subparsers.add_parser("grade", help="Grade a student's reply")
    grade_parser.add_argument("mark", type=int, help="Numeric mark")
    grade_parser.add_argument("comment", help="Grading feedback")
    grade_parser.add_argument("--question", help="Discord message ID of the question (optional, defaults to last posted)")

    # add
    add_parser = subparsers.add_parser("add", help="Add a course, topic, or question")
    add_subparsers = add_parser.add_subparsers(dest="add_command")

    # add course
    add_course = add_subparsers.add_parser("course", help="Add a course")
    add_course.add_argument("--part", required=True, help="Course part (IA, IB, II, III)")
    add_course.add_argument("--name", required=True, help="Course name")

    # add topic
    add_topic = add_subparsers.add_parser("topic", help="Add a topic to a course")
    add_topic.add_argument("--course_name", required=True, help="Course name")
    add_topic.add_argument("--name", required=True, help="Topic name")
    add_topic.add_argument("--description", help="Topic description")

    # add question
    add_question = add_subparsers.add_parser("question", help="Add a question to a topic")
    add_question.add_argument("--course_name", required=True, help="Course name")
    add_question.add_argument("--topic_name", required=True, help="Topic name")
    add_question.add_argument("--question", required=True, help="Question text")
    add_question.add_argument("--model_answer", required=True, help="Model answer")
    add_question.add_argument("--max_mark", type=int, required=True, help="Maximum possible mark")

    # list
    list_parser = subparsers.add_parser("list", help="List courses, topics, or questions")
    list_parser.add_argument("entity", choices=["courses", "topics", "questions"], help="What to list")
    list_parser.add_argument("--course_name", help="Filter by course name (topics, questions)")
    list_parser.add_argument("--topic_name", help="Filter by topic name (questions, requires --course_name)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "status":
        sys.exit(status.run(args.course))
    elif args.command == "post":
        sys.exit(post.run(args.question, args.answer, args.id, args.course,
                          args.max_mark, args.topic))
    elif args.command == "check":
        sys.exit(check.run(args.question))
    elif args.command == "grade":
        sys.exit(grade.run(args.mark, args.comment, args.question))
    elif args.command == "add":
        if not args.add_command:
            add_parser.print_help()
            sys.exit(1)
        sys.exit(add.run(args.add_command,
                         part=getattr(args, 'part', None),
                         name=getattr(args, 'name', None),
                         course_name=getattr(args, 'course_name', None),
                         topic_name=getattr(args, 'topic_name', None),
                         question=getattr(args, 'question', None),
                         model_answer=getattr(args, 'model_answer', None),
                         max_mark=getattr(args, 'max_mark', None),
                         description=getattr(args, 'description', None)))
    elif args.command == "list":
        sys.exit(list_cmd.run(args.entity, args.course_name, args.topic_name))


# Import commands at the top level to avoid circular imports
from sageask.commands import status
from sageask.commands import post
from sageask.commands import check
from sageask.commands import grade
from sageask.commands import add
from sageask.commands import list as list_cmd


if __name__ == "__main__":
    main()
