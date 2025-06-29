from flask import Flask
from flask_jwt_extended import JWTManager
from supabase import create_client, Client
from redis import Redis
from flask_apscheduler import APScheduler
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Supabase
    app.supabase = create_client(app.config["SUPABASE_URL"], app.config["SUPABASE_KEY"])

    # Initialize JWT
    jwt = JWTManager(app)

    # Initialize Redis
    app.redis = Redis.from_url(app.config["REDIS_URL"], decode_responses=True)

    # Initialize APScheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    # Register blueprints
    from .routes import (
        members,
        contributions,
        dues,
        penalties,
        transactions,
        income_expenses,
        payment_tracking,
        attendance
    )

    app.register_blueprint(members.bp)
    app.register_blueprint(contributions.bp)
    app.register_blueprint(dues.bp)
    app.register_blueprint(penalties.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(income_expenses.bp)
    app.register_blueprint(payment_tracking.bp)
    app.register_blueprint(attendance.bp)

    # Start custom scheduled tasks
    from .utils.scheduler import setup_scheduler
    setup_scheduler()

    return app
