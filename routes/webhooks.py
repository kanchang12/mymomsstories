"""
routes/webhooks.py — Payment webhooks
Stripe: /webhooks/stripe
"""
from flask import Blueprint, request, jsonify
from services.payments import handle_stripe_webhook, verify_stripe_webhook_signature

webhooks_bp = Blueprint("webhooks", __name__)


@webhooks_bp.route("/stripe", methods=["POST"])
def stripe_webhook():
    raw_body   = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")

    event = verify_stripe_webhook_signature(raw_body, sig_header)
    if event is None:
        return jsonify({"error": "Invalid signature"}), 401

    event_type  = event.get("type", "") if isinstance(event, dict) else event["type"]
    data_object = event["data"]["object"]

    result = handle_stripe_webhook(event_type, data_object)
    return jsonify(result), 200
