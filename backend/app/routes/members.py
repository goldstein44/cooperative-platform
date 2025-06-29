from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import create_app
from app.utils.paystack import Paystack
import uuid

bp = Blueprint("members", __name__, url_prefix="/api/members")

@bp.route("/register", methods=["POST"])
@jwt_required()
def register():
    data = request.get_json()
    current_user = get_jwt_identity()
    app = create_app()
    user_role = app.supabase.table("users").select("role").eq("id", current_user).execute().data[0]["role"]
    if user_role != "super_admin":
        return jsonify({"error": "Unauthorized"}), 403

    # Validate input
    email, name, phone, cooperative_id, amount = data.get("email"), data.get("name"), data.get("phone"), data.get("cooperative_id"), data.get("amount")
    if not all([email, name, phone, cooperative_id, amount]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Create user in Supabase Auth
        auth_response = app.supabase.auth.sign_up({"email": email, "password": data.get("password"), "phone": phone})
        user_id = auth_response.user.id

        # Insert into users table
        app.supabase.table("users").insert({
            "id": user_id,
            "email": email,
            "phone": phone,
            "name": name,
            "cooperative_id": cooperative_id,
            "role": "member",
            "status": "pending"
        }).execute()

        # Initiate Paystack payment
        reference = str(uuid.uuid4())
        paystack = Paystack()
        payment = paystack.initiate_payment(
            email=email,
            amount=amount,
            reference=reference,
            callback_url="https://your-frontend-url/callback"
        )

        # Record transaction
        app.supabase.table("transactions").insert({
            "cooperative_id": cooperative_id,
            "user_id": user_id,
            "amount": amount,
            "type": "registration",
            "paystack_ref": reference
        }).execute()

        return jsonify({
            "message": "Member registered, payment initiated",
            "payment_url": payment["data"]["authorization_url"]
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/approve/<user_id>", methods=["PATCH"])
@jwt_required()
def approve(user_id):
    current_user = get_jwt_identity()
    app = create_app()
    user_role = app.supabase.table("users").select("role").eq("id", current_user).execute().data[0]["role"]
    if user_role != "super_admin":
        return jsonify({"error": "Unauthorized"}), 403
    try:
        app.supabase.table("users").update({"status": "active"}).eq("id", user_id).execute()
        return jsonify({"message": "Member approved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
def delete(user_id):
    current_user = get_jwt_identity()
    app = create_app()
    user_role = app.supabase.table("users").select("role").eq("id", current_user).execute().data[0]["role"]
    if user_role != "super_admin":
        return jsonify({"error": "Unauthorized"}), 403
    try:
        app.supabase.table("users").update({"status": "inactive"}).eq("id", user_id).execute()
        return jsonify({"message": "Member deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<user_id>", methods=["GET"])
@jwt_required()
def get_member(user_id):
    current_user = get_jwt_identity()
    app = create_app()
    user = app.supabase.table("users").select("*").eq("id", user_id).execute().data
    if not user:
        return jsonify({"error": "Member not found"}), 404
    if current_user != user_id and app.supabase.table("users").select("role").eq("id", current_user).execute().data[0]["role"] not in ["super_admin", "admin"]:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(user[0]), 200
