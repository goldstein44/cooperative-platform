from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import create_app

bp = Blueprint("attendance", __name__, url_prefix="/api/attendance")

@bp.route("/<meeting_id>", methods=["POST"])
@jwt_required()
def record_attendance(meeting_id):
    data = request.get_json()
    current_user = get_jwt_identity()
    app = create_app()
    user = app.supabase.table("users").select("role, cooperative_id").eq("id", current_user).execute().data[0]
    if user["role"] not in ["super_admin", "admin"]:
        return jsonify({"error": "Unauthorized"}), 403
    user_id, status = data.get("user_id"), data.get("status")
    if not all([user_id, status]) or status not in ["present", "absent"]:
        return jsonify({"error": "Invalid input"}), 400
    try:
        app.supabase.table("attendance").insert({
            "cooperative_id": user["cooperative_id"],
            "user_id": user_id,
            "meeting_id": meeting_id,
            "status": status
        }).execute()
        return jsonify({"message": "Attendance recorded"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/<meeting_id>", methods=["GET"])
@jwt_required()
def get_attendance(meeting_id):
    current_user = get_jwt_identity()
    app = create_app()
    user = app.supabase.table("users").select("cooperative_id").eq("id", current_user).execute().data[0]
    meeting = app.supabase.table("meetings").select("cooperative_id").eq("id", meeting_id).execute().data
    if not meeting or meeting[0]["cooperative_id"] != user["cooperative_id"]:
        return jsonify({"error": "Unauthorized or meeting not found"}), 403
    try:
        attendance = app.supabase.table("attendance").select("*").eq("meeting_id", meeting_id).execute().data
        return jsonify(attendance), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500