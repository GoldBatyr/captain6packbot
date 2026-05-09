import requests
import json
import time

TOKEN = "8689947694:AAHFwTi7Yp5sjE2PcpJNfpEmq2VGUHkZA1Y"
CHAT_ID = "5701584585"
PHOTOS_DIR = "/Users/Batyr/Documents/exam_screens/photos"
QUESTIONS_FILE = "/Users/Batyr/Documents/exam_screens/questions.json"

photos = [
    {"file": "photo_30@27-09-2025_07-38-59.jpg", "q_index": 222},
    {"file": "photo_46@27-09-2025_07-40-06.jpg", "q_index": 390},
    {"file": "photo_47@27-09-2025_07-40-06.jpg", "q_index": 400},
    {"file": "photo_52@27-09-2025_07-40-06.jpg", "q_index": 429},
    {"file": "photo_50@27-09-2025_07-40-06.jpg", "q_index": 443},
    {"file": "photo_80@27-09-2025_07-41-21.jpg", "q_index": 455},
    {"file": "photo_81@27-09-2025_07-41-21.jpg", "q_index": 456},
    {"file": "photo_93@27-09-2025_07-46-45.jpg", "q_index": 468},
]

def send_photo(filepath):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(filepath, "rb") as f:
        response = requests.post(url, data={"chat_id": CHAT_ID}, files={"photo": f})
    result = response.json()
    if result.get("ok"):
        file_id = result["result"]["photo"][-1]["file_id"]
        return file_id
    else:
        print(f"  OSHIBKA: {result}")
        return None

with open(QUESTIONS_FILE) as f:
    data = json.load(f)

print(f"Zagruzheno {len(data)} voprosov\n")

for item in photos:
    filepath = f"{PHOTOS_DIR}/{item['file']}"
    q_num = item['q_index'] + 1
    print(f"Otpravlyayu Q{q_num}: {item['file']} ...")
    file_id = send_photo(filepath)
    if file_id:
        data[item['q_index']]['image'] = file_id
        print(f"  Q{q_num} file_id = {file_id}")
    else:
        print(f"  Q{q_num} — ne udalos poluchit file_id")
    time.sleep(1)

with open(QUESTIONS_FILE, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\nGotovo! questions.json obnovlen.")
