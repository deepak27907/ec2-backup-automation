@echo off
echo -----------------------------------------
echo Starting system backup to EC2...
echo -----------------------------------------

:: Step 1: Upload local folder to EC2
scp -i "<path-to-your-key.pem>" -r "<local-folder-path>" ec2-user@<EC2_PUBLIC_IP>:<remote-dir>

:: Step 2: Trigger Flask backup on EC2
curl -X POST http://<EC2_PUBLIC_IP>:5000/backup ^
 -H "Content-Type: application/json" ^
 -d "{\"folder\": \"<remote-dir>\"}"

echo -----------------------------------------
echo Backup completed.
pause
