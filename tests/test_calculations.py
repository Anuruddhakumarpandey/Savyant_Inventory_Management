import pytest
from decimal import Decimal

from app.calculations import calculate_total


def test_calculate_total():
    items = [
        {"qty": 2, "rate": 100},
        {"qty": 3, "rate": 50}
    ]

    assert calculate_total(items) == Decimal("350")


def test_empty_items():
    assert calculate_total([]) == Decimal("0")


def test_missing_items():
    with pytest.raises(ValueError):
        calculate_total(None)


def test_missing_quantity():
    items = [{"rate": 100}]

    with pytest.raises(ValueError):
        calculate_total(items)


def test_missing_rate():
    items = [{"qty": 2}]

    with pytest.raises(ValueError):
        calculate_total(items)


def test_zero_quantity():
    items = [{"qty": 0, "rate": 100}]

    with pytest.raises(ValueError):
        calculate_total(items)


def test_negative_quantity():
    items = [{"qty": -2, "rate": 100}]

    with pytest.raises(ValueError):
        calculate_total(items)


def test_negative_rate():
    items = [{"qty": 2, "rate": -100}]

    with pytest.raises(ValueError):
        calculate_total(items)


def test_invalid_rate():
    items = [{"qty": 2, "rate": "abc"}]

    with pytest.raises(ValueError):
        calculate_total(items)