"""Local synthetic business tools; the LLM remains live during SAM qualification.

Warehouse codes are random per tool-process startup. Expected values must come
from the actual observed lookup result, never from a prompt or fixed assertion.
These fixtures are for validation only, not production business integrations.
"""
import secrets
from typing import Any, Dict, Optional

# Opaque dependency values make canned final answers insufficient evidence.
_WAREHOUSE_ONE = "WH-" + secrets.token_hex(8)
_WAREHOUSE_TWO = "WH-" + secrets.token_hex(8)

_ORDERS = {
    "ORD-1001": {"order_id": "ORD-1001", "item": "Office monitor", "warehouse": _WAREHOUSE_ONE},
    "ORD-1002": {"order_id": "ORD-1002", "item": "Laptop dock", "warehouse": _WAREHOUSE_TWO},
}

_SHIPPING = {
    (_WAREHOUSE_ONE, "Copenhagen"): {"days": 1, "cost_eur": 4.90},
    (_WAREHOUSE_ONE, "Berlin"): {"days": 3, "cost_eur": 12.50},
    (_WAREHOUSE_TWO, "Copenhagen"): {"days": 2, "cost_eur": 5.40},
}


async def lookup_order(
    order_id: str,
    tool_context: Optional[Any] = None,
    tool_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Look up an order by id. Returns item and the warehouse it ships from.

    Args:
        order_id: The order identifier, e.g. "ORD-1001".
    """
    order = _ORDERS.get(order_id)
    if not order:
        return {"error": f"unknown order_id {order_id}", "known": list(_ORDERS)}
    return order


async def get_shipping_estimate(
    warehouse: str,
    destination: str,
    tool_context: Optional[Any] = None,
    tool_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Estimate shipping days and cost from a warehouse to a destination.

    Args:
        warehouse: Opaque warehouse code returned by lookup_order.
        destination: Destination city, e.g. "Copenhagen".
    """
    est = _SHIPPING.get((warehouse, destination))
    if not est:
        return {
            "error": f"no route {warehouse}->{destination}",
            "warehouse": warehouse,
            "destination": destination,
        }
    return {"warehouse": warehouse, "destination": destination, **est}


# JSON-Schema mirror for endpoint adapters that exercise the same fixture.
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_order",
            "description": "Look up an order by id; returns item and warehouse.",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "string"}},
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_shipping_estimate",
            "description": "Estimate shipping days/cost from a warehouse to a destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "warehouse": {"type": "string"},
                    "destination": {"type": "string"},
                },
                "required": ["warehouse", "destination"],
            },
        },
    },
]
