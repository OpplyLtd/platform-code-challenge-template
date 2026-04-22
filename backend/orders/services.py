"""Order fulfilment integration — product team → platform team handoff.

This module is where the product team signals that an order has transitioned.
How the event leaves Django and reaches the downstream workflow is the
platform team's call — implement the function body as you see fit, or change
where/how it's called.
"""
from __future__ import annotations


def publish_order_transitioned(order, previous_status: str) -> None:
    """Called on ``CONFIRMED -> PROCESSING``.

    The product team emits the event here. Everything downstream —
    transport, delivery guarantees, orchestration, retries, idempotency,
    visibility — is your design.

    You can fill in the body below, replace the call site in
    ``orders/views.py``, or rework the integration entirely. Up to you.
    """
    pass
