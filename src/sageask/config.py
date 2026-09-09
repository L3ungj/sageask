"""Load configuration from .env file using python-dotenv."""

import os
import sys
from dotenv import load_dotenv


def _resolve_data_dir():
    """Return the data directory containing .env and questions.db."""
    if d := os.environ.get("SAGEASK_DATA"):
        return d
    return os.path.expanduser("~/.local/share/sageask")


_DATA_DIR = _resolve_data_dir()


def _load_env():
    env_path = os.path.join(_DATA_DIR, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        return
    print(
        "error: .env not found — set SAGEASK_DATA or place .env in ~/.local/share/sageask/",
        file=sys.stderr,
    )
    sys.exit(1)


_load_env()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if DISCORD_BOT_TOKEN is None:
    print("error: DISCORD_BOT_TOKEN not set in .env", file=sys.stderr)
    sys.exit(1)

DISCORD_HOME_CHANNEL = os.getenv("DISCORD_HOME_CHANNEL")
if DISCORD_HOME_CHANNEL is None:
    print("error: DISCORD_HOME_CHANNEL not set in .env", file=sys.stderr)
    sys.exit(1)

DISCORD_ALLOWED_USERS_STR = os.getenv("DISCORD_ALLOWED_USERS")
if DISCORD_ALLOWED_USERS_STR is None:
    print("error: DISCORD_ALLOWED_USERS not set in .env", file=sys.stderr)
    sys.exit(1)

DISCORD_ALLOWED_USERS = [uid.strip() for uid in DISCORD_ALLOWED_USERS_STR.split(",") if uid.strip()]
