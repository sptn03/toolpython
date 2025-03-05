import requests
import threading
import time
from datetime import datetime
import random
import string
import base64
import hashlib

HU_ACCESSKEY_KEY = '1234567890'
HU_ACCESSKEY_CODE = 1234567890
HU_SECRET_KEY = '1234567890'
HU_SECRET_CODE = 0

# Biến toàn cục để đếm số lượng status 200
success_count = 0
# Lock để đồng bộ hóa việc tăng biến đếm
count_lock = threading.Lock()

def hu_encode(object_data):
    rawHash = "accessKey=" + HU_ACCESSKEY_KEY
    make_code = 0
    for key, item in object_data.items():
        if key == "signature":
            continue
        b64_item = base64.b64encode(item.encode()).decode()
        if item:
            len_item = len(b64_item)
            make_code += (ord(b64_item[0]) + ord(b64_item[len_item // 2]) + ord(b64_item[-1]))
        else:
            firstChar = key[0] if key else 'a'
            make_code += (ord(firstChar) + HU_ACCESSKEY_CODE)
    rawHash += hashlib.md5(str(make_code).encode()).hexdigest()
    return hashlib.md5(("sha256fake" + rawHash + HU_SECRET_KEY).encode()).hexdigest()

def send_request(request_id, url, payload, headers):
    global success_count
    start_time = time.time()
    print(f"Request {request_id} bắt đầu lúc: {datetime.now().strftime('%H:%M:%S.%f')}")
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        execution_time = time.time() - start_time
        print(f"Request {request_id} hoàn thành sau: {execution_time:.2f} giây")
        print(f"Kết quả request {request_id}: {response.text}")
        
        # Kiểm tra và đếm status 200
        if response.status_code == 200:
            with count_lock:
                success_count += 1
                
    except Exception as e:
        print(f"Request {request_id} gặp lỗi: {str(e)}")

def main():
    num_requests = 100  # Số lần gửi request
    
    print(f"Bắt đầu gửi {num_requests} request...")
    
    start_time = time.time()
    
    # Tạo 2 luồng và chạy cách nhau 100ms
    threads = []
    for request_id in range(1, num_requests + 1):
        # Sinh ra signature ngẫu nhiên cho mỗi request
        signature = hu_encode(payload)
        
        # Đảm bảo rằng signature được thêm vào payload
        payload = {
            'user_id': '208116',
            'amount': '121321',
            'description': 'Tiền khuyến mãi',
            'signature': signature
        }
        
        headers = {
        }
        
        thread = threading.Thread(target=send_request, args=(request_id, "https://hunocoin.hunonicpro.com//v1/Coins/ReceiveCoin", payload, headers))
        threads.append(thread)
        thread.start()
        
        if len(threads) >= 2:  # Giới hạn 2 luồng chạy đồng thời
            threads[0].join()
            threads.pop(0)
    
    # Đợi các luồng còn lại hoàn thành
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    print(f"\nTổng số request thành công (status 200): {success_count}")
    print(f"Tổng thời gian chạy: {total_time:.2f} giây")

if __name__ == "__main__":
    main()