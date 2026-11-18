import base64
import hashlib
import hmac
import json
import os
import smtplib
import urllib.request
from email.message import EmailMessage
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_APP_PASS = os.getenv("SMTP_APP_PASS", "")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/send-otp")
def send_otp():
    data = request.get_json(silent=True) or {}
    to_email = str(data.get("email", "")).strip()
    otp = str(data.get("otp", "")).strip()
    if not to_email or not otp:
        return jsonify({"sent": False, "error": "Email and OTP required"}), 400
    if not SMTP_USER or not SMTP_APP_PASS:
        return jsonify({"sent": False, "error": "Set SMTP_USER and SMTP_APP_PASS"}), 200

    msg = EmailMessage()
    msg["Subject"] = "BM FUTUROMIND AI — Your Verification OTP"
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.set_content(
        f"Hello,\n\nYour 6-digit verification OTP for BM FUTUROMIND AI Academy is: {otp}\n\n"
        f"Regards,\nBM FUTUROMIND AI (9150851916)"
    )
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_APP_PASS)
        server.send_message(msg)
    return jsonify({"sent": True})


@app.post("/api/razorpay/create-order")
def create_razorpay_order():
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        return jsonify({"error": "Razorpay keys not configured"}), 200
    data = request.get_json(silent=True) or {}
    payload = json.dumps({
        "amount": 100000,  # Rs. 1,000 INR in paise (One-Time Lifetime Access)
        "currency": "INR",
        "receipt": f"bm_{str(data.get('email', 'student'))[:24]}",
    }).encode("utf-8")
    auth = base64.b64encode(f"{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}".encode("utf-8")).decode("utf-8")
    req = urllib.request.Request(
        "https://api.razorpay.com/v1/orders",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Basic {auth}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        order = json.loads(resp.read().decode("utf-8"))
    return jsonify({"order_id": order.get("id"), "amount": 100000, "key_id": RAZORPAY_KEY_ID})


@app.post("/api/razorpay/verify")
def verify_razorpay_payment():
    if not RAZORPAY_KEY_SECRET:
        return jsonify({"verified": False}), 400
    data = request.get_json(silent=True) or {}
    order_id = str(data.get("razorpay_order_id", ""))
    payment_id = str(data.get("razorpay_payment_id", ""))
    signature = str(data.get("razorpay_signature", ""))
    expected = hmac.new(
        RAZORPAY_KEY_SECRET.encode("utf-8"),
        f"{order_id}|{payment_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return jsonify({"verified": hmac.compare_digest(expected, signature)})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
