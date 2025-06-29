import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import create_app

bp = Blueprint("payment_tracking", __name__, url_prefix="/api/payment-tracking")

@bp.route("/<task_id>", methods=["POST"])
@jwt_required()
def create_payment_tracking(task_id):
    data = request.get_json()
    current_user = get_jwt_identity()
    app = create_app()

    user = app.supabase.table("users").select("role, cooperative_id").eq("id", current_user).execute().data[0]
    if user["role"] not in ["super_admin", "admin"]:
        return jsonify({"error": "Unauthorized"}), 403

    user_id = data.get("user_id")
    amount_due = data.get("amount_due")

    if not all([user_id, amount_due]):
        return jsonify({"error": "Invalid input"}), 400

    try:
        app.supabase.table("payment_tracking").insert({
            "cooperative_id": user["cooperative_id"],
            "user_id": user_id,
            "task_id": task_id,
            "amount_due": amount_due,
            "amount_paid": 0,
            "status": "unpaid"
        }).execute()
        return jsonify({"message": "Payment tracking created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/<task_id>", methods=["GET"])
@jwt_required()
def get_payment_tracking(task_id):
    current_user = get_jwt_identity()
    app = create_app()

    user = app.supabase.table("users").select("cooperative_id").eq("id", current_user).execute().data[0]
    task = app.supabase.table("tasks").select("cooperative_id").eq("id", task_id).execute().data
    if not task or task[0]["cooperative_id"] != user["cooperative_id"]:
        return jsonify({"error": "Unauthorized or task not found"}), 403

    cache_key = f"payment_tracking:{task_id}"
    cached = app.redis.get(cache_key)
    if cached:
        return jsonify(json.loads(cached)), 200

    try:
        payments = app.supabase.table("payment_tracking").select("*").eq("task_id", task_id).execute().data
        app.redis.setex(cache_key, 300, json.dumps(payments))  # Cache for 5 minutes
        return jsonify(payments), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
