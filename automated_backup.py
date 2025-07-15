import boto3
import time
import subprocess
from datetime import datetime
import smtplib, ssl
import requests
from email.message import EmailMessage

# === CONFIGURATION ===

INSTANCE_ID = '<your-instance-id>'
 REGION = '<your-region>'
 BATCH_FILE = r"<path-to-batch-file>"
 LOG_FILE = r"<path-to-log-file>"
# --- Telegram Alert ---
 TELEGRAM_TOKEN = '<your-telegram-token>'
 TELEGRAM_CHAT_ID = '<your-chat-id>'
# --- Email Alert ---
 EMAIL_SENDER = '<your-email>'
 EMAIL_APP_PASSWORD = '<your-app-password>'
 EMAIL_RECEIVER = '<receiver-email>'


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
