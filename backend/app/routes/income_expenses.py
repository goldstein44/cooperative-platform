from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import create_app

bp = Blueprint("income_expenses", __name__, url_prefix="/api/income-expenses")

@bp.route("/", methods=["POST"])
@jwt_required()
def create_income_expense():
    data = request.get_json()
    current_user = get_jwt_identity()
    app = create_app()
    user = app.supabase.table("users").select("role, cooperative_id").eq("id", current_user).execute().data[0]
    if user["role"] not in ["super_admin", "admin"]:
        return jsonify({"error": "Unauthorized"}), 403
    amount, type, description = data.get("amount"), data.get("type"), data.get("description")
    if not all([amount, type, description]) or type not in ["income", "expense"]:
        return jsonify({"error": "Invalid input"}), 400
    try:
        app.supabase.table("income_expenses").insert({
            "cooperative_id": user["cooperative_id"],
            "type": type,
            "amount": amount,
            "description": description,
            "created_by": current_user
        }).execute()
        return jsonify({"message": f"{type.capitalize()} recorded"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/<cooperative_id>", methods=["GET"])
@jwt_required()
def get_income_expenses(cooperative_id):
    current_user = get_jwt_identity()
    app = create_app()
    user = app.supabase.table("users").select("cooperative_id").eq("id", current_user).execute().data[0]
    if user["cooperative_id"] != cooperative_id:
        return jsonify({"error": "Unauthorized"}), 403
    try:
        records = app.supabase.table("income_expenses").select("*").eq("cooperative_id", cooperative_id).execute().data
        return jsonify(records), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500