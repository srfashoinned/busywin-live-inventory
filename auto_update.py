import subprocess
import time
import os

print("Starting BusyWin → GitHub auto update...")

while True:

    # Step 1: Export BusyWin data
    print("Exporting items...")
    os.system("python export_items.py")

    # Step 2: Add changes
    subprocess.run(["git","add","items.json"])

    # Step 3: Commit
    subprocess.run(["git","commit","-m","Auto inventory update"])

    # Step 4: Push to GitHub
    subprocess.run(["git","push"])

    print("Inventory updated to GitHub")

    # Wait 5 minutes
    time.sleep(300)