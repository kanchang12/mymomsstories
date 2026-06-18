"""
routes/webhooks.py — Payment webhooks
PayPal: /webhooks/paypal
"""
import json
from flask import Blueprint, request, jsonify
from services.payments import handle_paypal_webhook, verify_paypal_webhook_signature

webhooks_bp = Blueprint("webhooks", __name__)


@webhooks_bp.route("/paypal", methods=["POST"])
def paypal_webhook():
    raw_body = request.get_data()

    if not verify_paypal_webhook_signature(dict(request.headers), raw_body):
        return jsonify({"error": "Invalid signature"}), 401

    try:
        event = json.loads(raw_body)
    except Exception:
        return jsonify({"error": "Bad JSON"}), 400

    event_type = event.get("event_type", "")
    resource   = event.get("resource", {})

    result = handle_paypal_webhook(event_type, resource)
    return jsonify(result), 200
