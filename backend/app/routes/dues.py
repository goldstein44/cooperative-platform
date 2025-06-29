from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint("dues", __name__, url_prefix="/api/dues")

@bp.route("/", methods=["POST"])
@jwt_required()
def create_due():
    data = request.get_json()
    current_user = get_jwt_identity()
    supabase = current_app.supabase

    user_result = supabase.table("users").select("role, cooperative_id").eq("id", current_user).execute()
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
        supabase.table("dues").insert({
            "cooperative_id": user["cooperative_id"],
            "user_id": user_id,
            "amount": amount,
            "due_date": due_date,
            "status": "pending"
        }).execute()
        return jsonify({"message": "Due created"}), 201
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
