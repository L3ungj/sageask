"""Discord REST API client."""

import requests

from sageask import config

DISCORD_API = "https://discord.com/api/v10"
USER_AGENT = "Sage-Asker/1.0"


def _headers():
    return {
        "Authorization": f"Bot {config.DISCORD_BOT_TOKEN}",
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
    }


def post_message(channel_id, content):
    """Post a message to a channel. Returns the Discord message ID."""
    r = requests.post(f"{DISCORD_API}/channels/{channel_id}/messages",
                      json={"content": content}, headers=_headers(), timeout=15)
    r.raise_for_status()
    return r.json()["id"]


def get_thread_messages(thread_id, limit=50):
    """Get messages from a thread (threads are channels)."""
    r = requests.get(f"{DISCORD_API}/channels/{thread_id}/messages?limit={limit}",
                     headers=_headers(), timeout=15)
    r.raise_for_status()
    return r.json()


def get_message(channel_id, message_id):
    """Get a single message."""
    r = requests.get(f"{DISCORD_API}/channels/{channel_id}/messages/{message_id}",
                     headers=_headers(), timeout=15)
    r.raise_for_status()
    return r.json()
