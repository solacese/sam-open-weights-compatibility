"""Deterministic mock tools for SAM open-weights model validation.

These are intentionally trivial and stateless. Their only job is to force the
model through the real agent tool-calling loop with a DEPENDENT chain:
`lookup_order` returns a warehouse code that `get_shipping_estimate` requires.

A model that fakes tool calling cannot pass, because it has no way to invent the
correct warehouse code ("WH-DK-02") without actually receiving lookup_order's
result and passing it back — which is exactly SAM's H3 (tool-result turn).

Wire these as SAM Python tools (see tests/configs/agent.yaml). Signatures follow
SAM's function-based tool convention: async, keyword args matching the schema,
optional tool_context / tool_config.
"""
from typing import Any, Dict, Optional

# Fixed data so assertions are deterministic.
_ORDERS = {
    "ORD-1001": {"order_id": "ORD-1001", "item": "Carlsberg Pilsner 24-pack", "warehouse": "WH-DK-02"},
    "ORD-1002": {"order_id": "ORD-1002", "item": "Tuborg Green 12-pack", "warehouse": "WH-DK-05"},
}

_SHIPPING = {
    ("WH-DK-02", "Copenhagen"): {"days": 1, "cost_eur": 4.90},
    ("WH-DK-02", "Berlin"): {"days": 3, "cost_eur": 12.50},
    ("WH-DK-05", "Copenhagen"): {"days": 2, "cost_eur": 5.40},
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
        warehouse: Warehouse code, e.g. "WH-DK-02" (comes from lookup_order).
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


# --- JSON-Schema mirror of the tools, for probe.sh / non-SAM harnesses ---
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
