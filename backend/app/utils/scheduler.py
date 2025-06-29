from app import create_app
from flask_apscheduler import APScheduler
import requests
from datetime import datetime, timedelta

def setup_scheduler():
    app = create_app()
    scheduler = APScheduler()
    scheduler.init_app(app)

    @scheduler.task("interval", id="send_reminders", seconds=86400)  # Run daily
    def send_reminders():
        with app.app_context():
            # Check overdue dues
            dues = app.supabase.table("dues").select("*, users(phone)").eq("status", "pending").lt("due_date", datetime.utcnow().isoformat()).execute().data
            for due in dues:
                phone = due["users"]["phone"]
                message = f"Reminder: Your due of ₦{due['amount']} is overdue. Please pay promptly."
                requests.post(
                    "https://api.termii.com/api/sms/send",
                    json={
                        "api_key": app.config["TERMII_API_KEY"],
                        "to": phone,
                        "from": app.config["TERMII_SENDER_ID"],
                        "sms": message,
                        "type": "plain",
                        "channel": "generic"
                    }
                )
            # Check upcoming meetings
            meetings = app.supabase.table("meetings").select("*").gt("date", datetime.utcnow().isoformat()).lt("date", (datetime.utcnow() + timedelta(days=1)).isoformat()).execute().data
            for meeting in meetings:
                users = app.supabase.table("users").select("phone").eq("cooperative_id", meeting["cooperative_id"]).execute().data
                for user in users:
                    phone = user["phone"]
                    message = f"Reminder: Meeting '{meeting['title']}' is scheduled for {meeting['date']}."
                    requests.post(
                        "https://api.termii.com/api/sms/send",
                        json={
                            "api_key": app.config["TERMII_API_KEY"],
                            "to": phone,
                            "from": app.config["TERMII_SENDER_ID"],
                            "sms": message,
                            "type": "plain",
                            "channel": "generic"
                        }
                    )

    scheduler.start()