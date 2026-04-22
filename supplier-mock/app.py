"""Mock supplier endpoint.

Represents the external supplier in the fulfilment flow:
- Accepts `POST /notify` with an order payload
- After a delay, POSTs lifecycle callbacks (confirmed / shipped / delivered)
  to a URL you provide in the notify body (`callback_url`)
- Exposes `GET /status/<order_id>` for pull-based consumers

Configurable via env vars (see README at repo root).
"""
from __future__ import annotations

import logging
import os
import random
import threading
import time

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

FAIL_RATE = float(os.environ.get("SUPPLIER_FAIL_RATE", "0.0"))
LATENCY_MS = int(os.environ.get("SUPPLIER_LATENCY_MS", "0"))
CONFIRMED_DELAY_S = int(os.environ.get("SUPPLIER_CONFIRMED_DELAY_S", "5"))
SHIPPED_DELAY_S = int(os.environ.get("SUPPLIER_SHIPPED_DELAY_S", "10"))
DELIVERED_DELAY_S = int(os.environ.get("SUPPLIER_DELIVERED_DELAY_S", "15"))

STATE: dict[str, str] = {}
STATE_LOCK = threading.Lock()


def _set_state(order_id: str, event: str) -> None:
    with STATE_LOCK:
        STATE[str(order_id)] = event


@app.route("/notify", methods=["POST"])
def notify():
    body = request.get_json(silent=True) or {}
    app.logger.info("notify received: %s", body)

    if LATENCY_MS:
        time.sleep(LATENCY_MS / 1000.0)

    if random.random() < FAIL_RATE:
        app.logger.info("simulated failure for order %s", body.get("order_id"))
        return jsonify({"error": "simulated supplier outage"}), 500

    order_id = body.get("order_id")
    callback_url = body.get("callback_url")
    if order_id is None:
        return jsonify({"error": "order_id is required"}), 400

    _set_state(order_id, "accepted")
    threading.Thread(
        target=_run_lifecycle,
        args=(str(order_id), callback_url),
        daemon=True,
    ).start()

    return jsonify({"status": "accepted", "order_id": order_id}), 202


@app.route("/status/<order_id>", methods=["GET"])
def status(order_id: str):
    with STATE_LOCK:
        return jsonify({"order_id": order_id, "state": STATE.get(str(order_id), "unknown")})


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"}), 200


def _run_lifecycle(order_id: str, callback_url: str | None) -> None:
    sequence = [
        ("confirmed", CONFIRMED_DELAY_S),
        ("shipped", SHIPPED_DELAY_S),
        ("delivered", DELIVERED_DELAY_S),
    ]
    for event, delay_s in sequence:
        time.sleep(delay_s)
        _set_state(order_id, event)
        if not callback_url:
            continue
        try:
            resp = requests.post(
                callback_url,
                json={"event": event, "order_id": order_id},
                timeout=5,
            )
            app.logger.info(
                "callback %s for order %s → %s %s",
                event,
                order_id,
                resp.status_code,
                callback_url,
            )
        except requests.RequestException as exc:
            app.logger.warning(
                "callback %s for order %s failed: %s",
                event,
                order_id,
                exc,
            )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
