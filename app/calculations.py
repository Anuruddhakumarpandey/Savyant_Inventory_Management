from decimal import Decimal, InvalidOperation


def calculate_total(items):

    if items is None:
        raise ValueError("Items are required.")

    total = Decimal("0")

    for index, item in enumerate(items, start=1):

        if not isinstance(item, dict):
            raise ValueError(f"Item {index} must be a dictionary.")

        if "qty" not in item or "rate" not in item:
            raise ValueError(f"Item {index} must contain qty and rate.")

        try:
            qty = Decimal(str(item["qty"]))
            rate = Decimal(str(item["rate"]))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError(f"Item {index} quantity and rate must be numeric.")

        if not qty.is_finite() or qty <= 0:
            raise ValueError(f"Item {index} quantity must be positive.")

        if not rate.is_finite() or rate < 0:
            raise ValueError(f"Item {index} rate must be non-negative.")

        total += qty * rate

    return total