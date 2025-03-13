import schedule
import time
import subprocess

def run_script():
    print("Running the script...")
    subprocess.run(["python", "scripts/main.py"])

# Schedule the script to run every 1 hour
schedule.every(1).hour.do(run_script)

while True:
    schedule.run_pending()
    time.sleep(1)