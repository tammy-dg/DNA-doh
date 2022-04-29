"""Synthesize person data."""

from datetime import date

from faker import Faker
from pydantic import BaseModel


# Fake object.
_FAKER = None


class PersonParams(BaseModel):
    """Params for person synthesis."""
    min_dob: date
    max_dob: date


def get_faker(seed=None):
    """Get (construct) global faker."""
    global _FAKER
    if _FAKER is None:
        assert seed is not None, "Faker not initialized"
        _FAKER = Faker(seed)
    return _FAKER


def rand_date_of_birth(params):
    """Create a random date of birth."""
    return get_faker().date_between_dates(date_start=params.min_dob, date_end=params.max_dob)
