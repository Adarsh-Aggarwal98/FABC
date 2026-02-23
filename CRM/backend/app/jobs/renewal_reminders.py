"""
Renewal Reminders Job
Processes daily renewal reminders for recurring services
"""
from flask import current_app


def process_renewal_reminders():
    """
    Process all due renewal reminders.
    Called by the scheduler daily at 8 AM.

    Returns:
        dict: Summary of processing results
    """
    from app.modules.services.services.renewal_service import RenewalService

    current_app.logger.info('=== Starting Daily Renewal Reminder Job ===')

    try:
        result = RenewalService.process_daily_reminders()

        current_app.logger.info(
            f'=== Renewal Reminder Job Complete === '
            f'Sent: {result["sent"]}, Failed: {result["failed"]}, Total: {result["total"]}'
        )

        return result

    except Exception as e:
        current_app.logger.error(f'Renewal reminder job failed: {str(e)}')
        raise


def run_manual_reminder_check():
    """
    Manually trigger the reminder check (for testing or admin use).

    Returns:
        dict: Summary of processing results
    """
    return process_renewal_reminders()
