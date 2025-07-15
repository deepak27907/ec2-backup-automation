import boto3
import time
import subprocess
from datetime import datetime
import smtplib, ssl
import requests
from email.message import EmailMessage

# === CONFIGURATION ===

INSTANCE_ID = 'i-02380a68908cccb8b'
REGION = 'ap-south-1'
BATCH_FILE = r"C:\Users\Acer\Desktop\backup_flask_python_project\backup_to_ec2.bat"
LOG_FILE = r"C:\Users\Acer\Desktop\backup_flask_python_project\backup_log.txt"

# --- Telegram Alert ---
TELEGRAM_TOKEN = '7983019316:AAE_IHLBbXKXj4VvQJyhNf-Wh4uJyeODkoI'
TELEGRAM_CHAT_ID = '5306879491'

# --- Email Alert ---
EMAIL_SENDER = 'ashokbairwa787874@gmail.com'
EMAIL_APP_PASSWORD = 'ulzptqmgqjkoqury'
EMAIL_RECEIVER = 'ashokcomputer.ac@gmail.com'


# === FUNCTIONS ===

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} {msg}\n")
    print(f"{timestamp} {msg}")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        requests.post(url, json=payload)
    except Exception as e:
        log("Telegram error: " + str(e))

def send_email(subject, body):
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        log("Email error: " + str(e))

def notify_all(msg):
    send_telegram(msg)
    send_email("EC2 Backup Alert", msg)


# === MAIN WORKFLOW ===

try:
    log("🔓 Starting EC2 instance...")
    ec2 = boto3.client('ec2', region_name=REGION)
    ec2.start_instances(InstanceIds=[INSTANCE_ID])

    log("⏳ Waiting for EC2 to be running...")
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[INSTANCE_ID])
    log("✅ EC2 is running. Waiting 60s for Flask to boot...")
    time.sleep(60)

    log("💾 Running Windows backup script...")
    result = subprocess.run(BATCH_FILE, shell=True)
    log("📁 Backup script finished with code: " + str(result.returncode))

    log("🛑 Stopping EC2 instance...")
    ec2.stop_instances(InstanceIds=[INSTANCE_ID])
    log("✅ EC2 instance stopped.")

    notify_all("✅ Backup completed successfully and EC2 stopped.")

except Exception as e:
    log("❌ ERROR: " + str(e))
    notify_all(f"❌ Backup failed!\n\nError: {e}")
