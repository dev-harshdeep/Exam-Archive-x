import math
import os
from flask import Blueprint, render_template, session, redirect,current_app,jsonify
from models.question_paper import QuestionPaper
from datetime import datetime
from models.restore import restore_backup
from models.backup import backup_database_and_files
from datetime import datetime


admin_bp = Blueprint('admin', __name__)

    
def get_last_backup_date():
    backup_files = os.listdir('/app/backupFiles')
    backup_dates = []
    for filename in backup_files:
        try:
            # Split the filename and extract the date and time part
            date_str = (filename.split('_')[1]+'_'+filename.split('_')[2]).replace('.tar.gz', '')
            date = datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
            current_app.logger.info(date)
            backup_dates.append(date)
        except IndexError:
            pass  # Skip filenames that do not match the expected format
    if not backup_dates:
        return datetime(2023, 5, 20, 15, 30, 0)  # Example date and time
    return max(backup_dates)

    # Suppose you retrieve the last backup date from a database
@admin_bp.route('/backup-manager', methods=['GET'])
def backupManager():
    backup_dir = '/app/backupFiles'  # Path to the backup directory
    backups = []
    if os.path.exists(backup_dir):
        backups_info = os.listdir(backup_dir)
        for backup in backups_info:
            name, ext = os.path.splitext(backup)
            # Splitting filename to get date and time
            parts = name.split('_')
            date = parts[1]
            # time = parts[2]
            time = parts[2].split('.')[0]  # Remove milliseconds
            # Convert time to 12-hour format
            time_obj = datetime.strptime(time, "%H-%M-%S")
            time_12h_format = time_obj.strftime("%I:%M:%S %p")
            # Extracting compression ratio if available
            compression_ratio = "N/A"
            # Extracting encryption status if available
            encryption_status = "Not encrypted"
            # Constructing backup dictionary
            backup_info = {
                "name": backup,
                "date": date,
                "time": time_12h_format,
                "size": str(round(int (os.path.getsize(os.path.join(backup_dir, backup)) )/(1024 * 1024),3))+" MB",
                "compression_ratio": compression_ratio,
                "encryption_status": encryption_status
            }
            backups.append(backup_info)
    return render_template('backupDashboard.html', backups=backups)


@admin_bp.route('/trigger-backup', methods=['GET'])
def trigger_backup():
    current_app.logger.info("request recieved for backup")
    try:
        backup_database_and_files()
        current_app.logger.info("backup successfull")
        return 'Backup triggered successfully', 200
    except Exception as e:
        current_app.logger.info(e)
        return f'Error triggering backup: {e}', 500
    
@admin_bp.route('/backups', methods=['GET'])
def list_backups():
    backup_dir = '/app/backupFiles'  # Path to the backup directory
    backups = []
    if os.path.exists(backup_dir):
        backups = os.listdir(backup_dir)
    return render_template('backups.html', backups=backups)

@admin_bp.route('/restore_backup/<backup_name>', methods=['POST'])
def restore_backup_endpoint(backup_name):
    # Construct the full path to the backup file
    backup_dir = '/app/backupFiles/' # Assuming you set up a configuration for the backup directory
    backup_path =backup_dir+ backup_name

    # Check if the backup file exists
    if os.path.exists(backup_path):
        restore_backup(backup_path)
        return jsonify({'status': 'success', 'message': f'Backup {backup_name} restored successfully'})
    else:
        # Return response indicating failure if the backup file does not exist
        return jsonify({'status': 'error', 'message': f'Backup {backup_name} does not exist'})

@admin_bp.route('/dashboard')
def dashboard():
    # Query the database to count the number of question papers
    num_papers = QuestionPaper.query.count()

    # Get the size of the folder where question papers are stored
    folder_path =  os.path.join('/app/paperFiles')
    folder_size = get_folder_size(folder_path)

    # Convert folder size to a human-readable format (e.g., KB, MB, GB)
    folder_size_gb =round( folder_size / (1024 * 1024 ),2)  # Convert bytes to MB

    return render_template('admin/dashboard.html', num_papers=num_papers, folder_size_gb=folder_size_gb , last_backup_date=get_last_backup_date())

def get_folder_size(folder_path):
    # Get the size of the specified folder
    folder_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            folder_size += os.path.getsize(file_path)
        break  # We only need the size of the immediate folder, so break after the first iteration
    return folder_size
