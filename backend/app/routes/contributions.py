from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint("contributions", __name__, url_prefix="/api/contributions")

@bp.route("/", methods=["POST"])
@jwt_required()
def create_contribution():
    data = request.get_json()
    current_user = get_jwt_identity()
    supabase = current_app.supabase

    user_result = supabase.table("users").select("role, cooperative_id").eq("id", current_user).execute()
    if not user_result.data:
        return jsonify({"error": "User not found"}), 404

    user = user_result.data[0]

    user_id = data.get("user_id", current_user)
    amount = data.get("amount")
    type = data.get("type")

    if user["role"] not in ["super_admin", "admin"] and user_id != current_user:
        return jsonify({"error": "Unauthorized"}), 403

    if not all([amount, type]) or type not in ["weekly", "monthly"]:
        return jsonify({"error": "Invalid input"}), 400

    try:
        supabase.table("contributions").insert({
            "user_id": user_id,
            "cooperative_id": user["cooperative_id"],
            "amount": amount,
            "type": type,
            "status": "pending"
        }).execute()
        return jsonify({"message": "Contribution created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/<cooperative_id>", methods=["GET"])
@jwt_required()
def get_contributions(cooperative_id):
    current_user = get_jwt_identity()
    supabase = current_app.supabase

    user_result = supabase.table("users").select("cooperative_id").eq("id", current_user).execute()
    if not user_result.data:
        return jsonify({"error": "User not found"}), 404

    user = user_result.data[0]
    if user["cooperative_id"] != cooperative_id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        contributions = supabase.table("contributions").select("*").eq("cooperative_id", cooperative_id).execute().data
        return jsonify(contributions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.paystack import Paystack
import uuid

bp = Blueprint("contributions", __name__, url_prefix="/api/contributions")

@bp.route("/", methods=["POST"])
@jwt_required()
def create_contribution():
    data = request.get_json()
    current_user = get_jwt_identity()
    supabase = current_app.supabase

    user_result = supabase.table("users").select("role, cooperative_id, email").eq("id", current_user).execute()
    if not user_result.data:
        return jsonify({"error": "User not found"}), 404

    user = user_result.data[0]

    user_id = data.get("user_id", current_user)
    amount = data.get("amount")
    contribution_type = data.get("type")

    if user["role"] not in ["super_admin", "admin"] and user_id != current_user:
        return jsonify({"error": "Unauthorized"}), 403

    if not all([amount, contribution_type]) or contribution_type not in ["weekly", "monthly"]:
        return jsonify({"error": "Invalid input"}), 400

    try:
        # Generate payment reference
        reference = str(uuid.uuid4())

        # Insert contribution with status pending
        supabase.table("contributions").insert({
            "user_id": user_id,
            "cooperative_id": user["cooperative_id"],
            "amount": amount,
            "type": contribution_type,
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
            "type": "contribution",
            "paystack_ref": reference
        }).execute()

        return jsonify({
            "message": "Contribution created and payment initiated",
            "payment_url": payment["data"]["authorization_url"]
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<cooperative_id>", methods=["GET"])
@jwt_required()
def get_contributions(cooperative_id):
    current_user = get_jwt_identity()
    supabase = current_app.supabase

    user_result = supabase.table("users").select("cooperative_id").eq("id", current_user).execute()
    if not user_result.data:
        return jsonify({"error": "User not found"}), 404

    user = user_result.data[0]
    if user["cooperative_id"] != cooperative_id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        contributions = supabase.table("contributions").select("*").eq("cooperative_id", cooperative_id).execute().data
        return jsonify(contributions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

