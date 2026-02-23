"""
Background Jobs Module
Uses APScheduler for scheduling recurring tasks
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app
import atexit

scheduler = None


def init_scheduler(app):
    """
    Initialize the APScheduler with the Flask app.

    Args:
        app: Flask application instance
    """
    global scheduler

    # Only initialize once
    if scheduler is not None:
        return scheduler

    scheduler = BackgroundScheduler()

    # Add jobs
    from app.jobs.renewal_reminders import process_renewal_reminders

    # Run renewal reminders daily at 8 AM
    scheduler.add_job(
        func=lambda: run_with_app_context(app, process_renewal_reminders),
        trigger=CronTrigger(hour=8, minute=0),
        id='daily_renewal_reminders',
        name='Process daily renewal reminders',
        replace_existing=True
    )

    # Start the scheduler
    scheduler.start()
    app.logger.info('APScheduler started - Daily renewal reminders scheduled for 8:00 AM')

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: shutdown_scheduler())

    return scheduler


def run_with_app_context(app, func):
    """
    Run a function within the Flask app context.

    Args:
        app: Flask application instance
        func: Function to run
    """
    with app.app_context():
        try:
            return func()
        except Exception as e:
            app.logger.error(f'Scheduled job error: {str(e)}')


def shutdown_scheduler():
    """Shut down the scheduler gracefully"""
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        scheduler = None


def get_scheduler():
    """Get the scheduler instance"""
    return scheduler
