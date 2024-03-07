import requests
import logging
from datetime import datetime, timedelta
from models.backup import backup_database_and_files
from flask import Blueprint, request, jsonify , current_app , abort
from models.auto_backup import AutoBackupSettings
from models.database import db
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

auto_backup_bp = Blueprint('auto_backup', __name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

scheduler = BackgroundScheduler()
scheduler.start()

@auto_backup_bp.route('/auto-backup-settings', methods=['GET'])
def get_auto_backup_settings():
    settings = AutoBackupSettings.query.first()
    if settings:
        return jsonify({
            'time_frame': settings.time_frame,
            'frequency': settings.frequency,
            'enabled': settings.enabled
        })
    else:
        return jsonify({}), 404

# Error Handlingx
def handle_scheduler_error(e):
    # Log the error or take appropriate action
    current_app.logger.error(f"Error scheduling backup job: {e}")
    abort(500, description="Internal server error occurred while scheduling backup job")

# Data Validation
def validate_auto_backup_data(data):
    enabled = data.get('enabled', False)
    time_frame = data.get('time_frame')
    frequency = data.get('frequency')

    # Validate time frame
    valid_time_frames = ['Yearly', 'Monthly', 'Weekly', 'Daily']
    if time_frame not in valid_time_frames:
        abort(400, description="Invalid time frame")

    # Validate frequency if enabled
    if enabled:
        if frequency == '' or frequency is None or  int(frequency) <= 0:
            abort(400, description="Frequency must be a positive integer")

@auto_backup_bp.route('/auto-backup-settings', methods=['POST'])
def set_auto_backup_settings():
    data = request.json

    # Validate input data
    validate_auto_backup_data(data)

    time_frame = data.get('time_frame')
    enabled = data.get('enabled', False)
    if enabled:
        frequency = int(data.get('frequency'))
    else:
        frequency = 0  # Provide a default value

    settings = AutoBackupSettings.query.first()
    if settings:
        settings.time_frame = time_frame
        settings.frequency = frequency
        settings.enabled = enabled
    else:
        settings = AutoBackupSettings(time_frame=time_frame, frequency=frequency, enabled=enabled)
        db.session.add(settings)
    db.session.commit()

    # Reschedule backup job if enabled
    if enabled:
        try:
            reschedule_backup_job(time_frame, frequency)
        except Exception as e:
            handle_scheduler_error(e)
    else:
        scheduler.remove_all_jobs()

    return jsonify({'message': 'Auto backup settings saved'}), 200

# Error handlers
@auto_backup_bp.errorhandler(400)
def bad_request_error(e):
    return jsonify({'message': str(e)}), 400

@auto_backup_bp.errorhandler(500)
def internal_server_error(e):
    return jsonify({'message': 'Internal server error occurred'}), 500

def backup_job():
    url = 'http://127.0.0.1:5000/admin/trigger-backup' 
    response = requests.get(url)


def reschedule_backup_job(time_frame, frequency):
    # Remove existing job
    scheduler.remove_all_jobs()

    # Calculate the next backup time
    next_backup_time = calculate_next_backup_time(time_frame, frequency)

    # Schedule new job
    trigger = DateTrigger(run_date=next_backup_time)
    scheduler.add_job(backup_job, trigger=trigger, id='backup_job')
# This function will run before each request to any endpoint within the blueprint
def schedule_initial_backup_job():
    # Put your logic here to schedule the initial backup job if enabled
    settings = AutoBackupSettings.query.first()
    if settings and settings.enabled:
        reschedule_backup_job(settings.time_frame, settings.frequency)
        current_app.logger.info("Initial Job Schduled ")

@auto_backup_bp.route('/next-auto-backup-time', methods=['GET'])
def get_next_auto_backup_time():
    settings = AutoBackupSettings.query.first()
    if settings and settings.enabled:
        next_backup_time = calculate_next_backup_time(settings.time_frame, settings.frequency)
        return jsonify({'next_backup_time': next_backup_time.isoformat()}), 200
    else:
        return jsonify({'message': 'Auto backup is not enabled'}), 400
def calculate_next_backup_time(time_frame, frequency):
    now = datetime.now()
    next_backup_time = None

    # Calculate the interval based on the frequency
    interval = 1 / frequency

    # Set the initial next backup time based on the time frame
    if time_frame == 'Yearly':
        next_backup_time = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif time_frame == 'Monthly':
        next_backup_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif time_frame == 'Weekly':
        day_diff = (7 - now.weekday()) % 7
        next_backup_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day_diff)
    elif time_frame == 'Daily':
        next_backup_time = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Check if the current time is already past the scheduled time for today
    if now > next_backup_time:
        # If so, move the next backup time to the next occurrence based on the frequency
        while now > next_backup_time:
            next_backup_time += timedelta(days=interval)

    return next_backup_time

