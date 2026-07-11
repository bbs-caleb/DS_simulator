import random


def username_generator(n, first_names=None, last_names=None):
    """Generate user dictionaries with sequential unique IDs."""
    if first_names is None:
        first_names = ["Alex", "Maria", "John", "Anna"]

    if last_names is None:
        last_names = ["Smith", "Brown", "Wilson", "Taylor"]

    for user_id in range(1, n + 1):
        yield {
            "id": user_id,
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
        }


def data_generator(n):
    """Generate pairs of an index and a random integer from 0 to 100."""
    for x_value in range(n):
        yield x_value, random.randint(0, 100)
