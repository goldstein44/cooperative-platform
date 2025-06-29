from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.paystack import Paystack
import uuid

bp = Blueprint("dues", __name__, url_prefix="/api/dues")

@bp.route("/", methods=["POST"])
@jwt_required()
def create_due():
    data = request.get_json()
    current_user = get_jwt_identity()
    supabase = current_app.supabase

    user_result = supabase.table("users").select("role, cooperative_id, email").eq("id", current_user).execute()
    if not user_result.data:
        return jsonify({"error": "User not found"}), 404

    user = user_result.data[0]
    if user["role"] not in ["super_admin", "admin"]:
        return jsonify({"error": "Unauthorized"}), 403

    amount = data.get("amount")
    due_date = data.get("due_date")
    user_id = data.get("user_id")

    if not all([amount, due_date, user_id]):
        return jsonify({"error": "Invalid input"}), 400

    try:
        # Generate reference
        reference = str(uuid.uuid4())

        # Insert due record
        supabase.table("dues").insert({
            "cooperative_id": user["cooperative_id"],
            "user_id": user_id,
            "amount": amount,
            "due_date": due_date,
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
            "type": "due",
            "paystack_ref": reference
        }).execute()

        return jsonify({
            "message": "Due created, payment initiated",
            "payment_url": payment["data"]["authorization_url"]
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<cooperative_id>", methods=["GET"])
@jwt_required()
def get_dues(cooperative_id):
    current_user = get_jwt_identity()
    supabase = current_app.supabase

    user_result = supabase.table("users").select("cooperative_id").eq("id", current_user).execute()
    if not user_result.data:
        return jsonify({"error": "User not found"}), 404

    user = user_result.data[0]
    if user["cooperative_id"] != cooperative_id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        dues = supabase.table("dues").select("*").eq("cooperative_id", cooperative_id).execute().data
        return jsonify(dues), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
