import re
from typing import List


VALID_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
)


def valid_emails(strings: List[str]) -> List[str]:
    """Take list of potential emails and return only valid ones."""
    return [email for email in strings if VALID_EMAIL_REGEX.fullmatch(email)]
