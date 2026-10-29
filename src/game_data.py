"""Load and validate challenge content from the clean CSV."""
from pathlib import Path
import csv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "game_challenges.csv"
REQUIRED_FIELDS = {
    "challenge_id", "challenge_name", "zone_name", "cs_topic",
    "learning_objective", "player_objective", "hint_text",
}

def load_challenge(challenge_id="RAM-001", path=DEFAULT_DATA_PATH):
    """Return one challenge as a dict; fail loudly if the data is invalid."""
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError("Challenge CSV is missing a header row.")
        missing = REQUIRED_FIELDS.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"Challenge CSV missing required fields: {sorted(missing)}")
        rows = list(reader)

    ids = [row["challenge_id"].strip() for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("challenge_id values must be unique.")
    matches = [row for row in rows if row["challenge_id"].strip() == challenge_id]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {challenge_id!r} row; found {len(matches)}.")

    challenge = {key: (value or "").strip() for key, value in matches[0].items()}
    for field in ("challenge_name", "learning_objective", "player_objective", "hint_text"):
        if not challenge.get(field):
            raise ValueError(f"{challenge_id} has an empty required value: {field}")
    return challenge
