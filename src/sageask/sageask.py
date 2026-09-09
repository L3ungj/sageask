"""SageAsk CLI — post questions to Discord, check replies."""

import argparse
import sys
from sageask import config, db, discord


def main():
    parser = argparse.ArgumentParser(prog="sageask", description="SageAsk: post questions to Discord, check replies")
    subparsers = parser.add_subparsers(dest="command")

    # status
    status_parser = subparsers.add_parser("status", help="Show question bank status")
    status_parser.add_argument("--course", type=int, help="Filter by course ID")

    # post
    post_parser = subparsers.add_parser("post", help="Post next unanswered (or specified) question")
    post_parser.add_argument("--course", type=int, help="Filter by course ID")
    post_parser.add_argument("--question", "-q", help="Question text to post (requires --answer)")
    post_parser.add_argument("--answer", "-a", help="Model answer (requires --question)")
    post_parser.add_argument("--id", type=int, help="Specific question ID to post")

    # check
    check_parser = subparsers.add_parser("check", help="Check for user's reply")
    check_parser.add_argument("--question", help="Discord message ID of the question (optional, defaults to last posted)")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new question to the bank")
    add_parser.add_argument("part", help="Course part (IA, IB, II, III)")
    add_parser.add_argument("course_name", help="Course name")
    add_parser.add_argument("question", help="Question text")

    # grade
    grade_parser = subparsers.add_parser("grade", help="Grade a student's reply")
    grade_parser.add_argument("mark", type=int, help="Numeric mark")
    grade_parser.add_argument("comment", help="Grading feedback")
    grade_parser.add_argument("--question", help="Discord message ID of the question (optional, defaults to last posted)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "status":
        sys.exit(status.run(args.course))
    elif args.command == "post":
        sys.exit(post.run(args.question, args.answer, args.id, args.course))
    elif args.command == "check":
        sys.exit(check.run(args.question))
    elif args.command == "grade":
        sys.exit(grade.run(args.mark, args.comment, args.question))
    elif args.command == "add":
        sys.exit(add.run(args.part, args.course_name, args.question))


# Import commands at the top level to avoid circular imports
from sageask.commands import status
from sageask.commands import post
from sageask.commands import check
from sageask.commands import grade
from sageask.commands import add


if __name__ == "__main__":
    main()
