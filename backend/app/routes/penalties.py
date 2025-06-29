from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.paystack import Paystack
import uuid

bp = Blueprint("penalties", __name__, url_prefix="/api/penalties")

@bp.route("/", methods=["POST"])
@jwt_required()
def create_penalty():
    data = request.get_json()
    current_user = get_jwt_identity()
    app = current_app
    supabase = app.supabase

    user_result = supabase.table("users").select("role, cooperative_id, email").eq("id", current_user).execute()
    if not user_result.data:
        return jsonify({"error": "User not found"}), 404

    user = user_result.data[0]

    if user["role"] not in ["super_admin", "admin"]:
        return jsonify({"error": "Unauthorized"}), 403

    amount = data.get("amount")
    reason = data.get("reason")
    user_id = data.get("user_id")

    if not all([amount, reason, user_id]):
        return jsonify({"error": "Invalid input"}), 400

    try:
        # Generate payment reference
        reference = str(uuid.uuid4())

        # Insert penalty record
        supabase.table("penalties").insert({
            "user_id": user_id,
            "cooperative_id": user["cooperative_id"],
            "amount": amount,
            "reason": reason,
            "status": "pending",
            "paystack_ref": reference
        }).execute()

        # Initiate Paystack payment
        paystack = Paystack()
        payment = paystack.initiate_payment(
            email=user["email"],
            amount=amount,
            reference=reference,
            callback_url="https://your-frontend-url/callback"
        )

        # Log transaction
        supabase.table("transactions").insert({
            "cooperative_id": user["cooperative_id"],
            "user_id": user_id,
            "amount": amount,
            "type": "penalty",
            "paystack_ref": reference
        }).execute()

        return jsonify({
            "message": "Penalty issued and payment initiated",
            "payment_url": payment["data"]["authorization_url"]
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<cooperative_id>", methods=["GET"])
@jwt_required()
def get_penalties(cooperative_id):
    current_user = get_jwt_identity()
    app = current_app
    supabase = app.supabase

    user_result = supabase.table("users").select("cooperative_id").eq("id", current_user).execute()
    if not user_result.data:
        return jsonify({"error": "User not found"}), 404

    user = user_result.data[0]
    if user["cooperative_id"] != cooperative_id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        penalties = supabase.table("penalties").select("*").eq("cooperative_id", cooperative_id).execute().data
        return jsonify(penalties), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
