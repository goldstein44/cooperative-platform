from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import create_app

bp = Blueprint("penalties", __name__, url_prefix="/api/penalties")

@bp.route("/", methods=["POST"])
@jwt_required()
def create_penalty():
    data = request.get_json()
    current_user = get_jwt_identity()
    app = create_app()
    user = app.supabase.table("users").select("role, cooperative_id").eq("id", current_user).execute().data[0]
    if user["role"] not in ["super_admin", "admin"]:
        return jsonify({"error": "Unauthorized"}), 403
    amount, reason, user_id = data.get("amount"), data.get("reason"), data.get("user_id")
    if not all([amount, reason, user_id]):
        return jsonify({"error": "Invalid input"}), 400
    try:
        app.supabase.table("penalties").insert({
            "user_id": user_id,
            "cooperative_id": user["cooperative_id"],
            "amount": amount,
            "reason": reason,
            "status": "pending"
        }).execute()
        return jsonify({"message": "Penalty issued"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/<cooperative_id>", methods=["GET"])
@jwt_required()
def get_penalties(cooperative_id):
    current_user = get_jwt_identity()
    app = create_app()
    user = app.supabase.table("users").select("cooperative_id").eq("id", current_user).execute().data[0]
    if user["cooperative_id"] != cooperative_id:
        return jsonify({"error": "Unauthorized"}), 403
    try:
        penalties = app.supabase.table("penalties").select("*").eq("cooperative_id", cooperative_id).execute().data
        return jsonify(penalties), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500