"""Test person data synthesis."""

from datetime import date

from pytest import fixture
from faker import Faker

from dnadoh.synth_person import PersonParams, get_faker, rand_date_of_birth


@fixture
def faker():
    return get_faker(12345)


@fixture
def params():
    now = date.today()
    return PersonParams(
        min_dob = date(now.year - 100, now.month, 1),
        max_dob = date(now.year - 1, now.month, 2)
    )


def test_person_date_of_birth(faker, params):
    for _ in range(3):
        dob = rand_date_of_birth(params)
        assert params.min_dob <= dob <= params.max_dob
