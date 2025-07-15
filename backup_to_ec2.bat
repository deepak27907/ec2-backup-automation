@echo off
echo -----------------------------------------
echo Starting system backup to EC2...
echo -----------------------------------------

:: Step 1: Upload local folder to EC2
scp -i "C:\Users\Acer\Downloads\mykey.pem" -r "C:\Users\Acer\Desktop\Tasks" ec2-user@13.203.12.236:/home/ec2-user/my_windows_files

:: Step 2: Trigger Flask backup on EC2
curl -X POST http://13.203.12.236:5000/backup ^
 -H "Content-Type: application/json" ^
 -d "{\"folder\": \"/home/ec2-user/my_windows_files\"}"

echo -----------------------------------------
echo Backup completed.
pause
