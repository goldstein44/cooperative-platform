from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import create_app
from app.utils.paystack import Paystack  # Ensure this path is correct

bp = Blueprint("transactions", __name__, url_prefix="/api/transactions")

@bp.route("/", methods=["POST"])
@jwt_required()
def create_transaction():
    data = request.get_json()
    current_user = get_jwt_identity()
    app = create_app()
    
    user = app.supabase.table("users").select("role, cooperative_id").eq("id", current_user).execute().data[0]
    
    if user["role"] not in ["super_admin", "admin"]:
        return jsonify({"error": "Unauthorized"}), 403

    amount = data.get("amount")
    type = data.get("type")
    user_id = data.get("user_id")
    paystack_ref = data.get("paystack_ref")

    if not all([amount, type]) or type not in ["contribution", "due", "penalty", "registration", "other"]:
        return jsonify({"error": "Invalid input"}), 400

    try:
        app.supabase.table("transactions").insert({
            "cooperative_id": user["cooperative_id"],
            "user_id": user_id,
            "amount": amount,
            "type": type,
            "paystack_ref": paystack_ref
        }).execute()
        return jsonify({"message": "Transaction recorded"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/<cooperative_id>", methods=["GET"])
@jwt_required()
def get_transactions(cooperative_id):
    current_user = get_jwt_identity()
    app = create_app()
    
    user = app.supabase.table("users").select("cooperative_id").eq("id", current_user).execute().data[0]
    
    if user["cooperative_id"] != cooperative_id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        transactions = app.supabase.table("transactions").select("*").eq("cooperative_id", cooperative_id).execute().data
        return jsonify(transactions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/paystack/webhook", methods=["POST"])
def paystack_webhook():
    app = create_app()
    data = request.get_json()
    event = data.get("event")

    if event == "charge.success":
        reference = data["data"]["reference"]
        amount = data["data"]["amount"] / 100  # Convert from kobo to naira
        metadata = data["data"].get("metadata", {})
        user_id = metadata.get("user_id")
        cooperative_id = metadata.get("cooperative_id")
        payment_type = metadata.get("type")

        try:
            # Verify payment
            paystack = Paystack()
            verification = paystack.verify_payment(reference)

            if verification["data"]["status"] == "success":
                # Update appropriate table
                if payment_type == "registration":
                    app.supabase.table("users").update({"status": "active"}).eq("id", user_id).execute()
                elif payment_type == "contribution":
                    app.supabase.table("contributions").update({"status": "paid"}).eq("paystack_ref", reference).execute()
                elif payment_type == "due":
                    app.supabase.table("dues").update({"status": "paid"}).eq("paystack_ref", reference).execute()
                elif payment_type == "penalty":
                    app.supabase.table("penalties").update({"status": "paid"}).eq("paystack_ref", reference).execute()

                # Record transaction
                app.supabase.table("transactions").insert({
                    "cooperative_id": cooperative_id,
                    "user_id": user_id,
                    "amount": amount,
                    "type": payment_type,
                    "paystack_ref": reference
                }).execute()

            return jsonify({"message": "Webhook processed"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Event not handled"}), 200
