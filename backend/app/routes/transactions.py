from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import create_app

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
    amount, type, user_id, paystack_ref = data.get("amount"), data.get("type"), data.get("user_id"), data.get("paystack_ref")
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