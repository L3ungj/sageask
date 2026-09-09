"""Check command — check for replies in the thread."""

import sys

from sageask import db, config, discord


def run(question_discord_id=None):
    """Check for replies in the thread of the given Discord message ID.
    If question_discord_id is None, checks the most recently posted question.
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
    finally:
        conn.close()

    message_id = q["discord_id"]

    conn = db.get_db()
    try:
        try:
            messages = discord.get_thread_messages(message_id, limit=50)
        except discord.DiscordAPIError as e:
            if e.status_code == 404:
                print("No thread found for this question yet. Create a thread from the message in Discord first.")
                return 0
            raise

        allowed_replies = []
        for msg in messages:
            author_id = msg.get("author", {}).get("id")
            if author_id not in config.DISCORD_ALLOWED_USERS:
                continue
            if msg.get("id") == message_id or msg.get("type") != 0:
                continue
            allowed_replies.append(msg)

        if allowed_replies:
            latest = allowed_replies[-1]
            reply_content = latest.get("content", "").strip()
            timestamp = latest.get("timestamp", "")

            db.mark_replied(conn, q["id"], reply_content, timestamp)
            author = latest.get("author", {}).get("username", "unknown")
            print(f"{author} replied: {reply_content}")
        else:
            print("No replies yet in the thread.")
    finally:
        conn.close()

    return 0
