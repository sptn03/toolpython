import requests

def get_shopee_product(item_id, shop_id):
    url = f"https://shopee.vn/api/v4/pdp/get_pc"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'vi-VN,vi;q=0.9',
        'd-nonptcha-sync': 'AAAGyDfLTzcEGRU4NmRiNDBhMjVkZDU0NGE1OGIwYTY3ZWIyYTc2YTE3NjUyMmE0ZjU4NjZiODRlZTZhNzYyNDQyNWI0YzBhODFmZDE3ODQ5YTk5YWZmNDYyOWJiNTM0Mjc0ZGRjZjRjNTM0MjE4Yjk4NjI0OWQ0ZDAwYmE5MDc2MjEyM2MyZDVmYgAG6jJEh6Z/viPWcAQABn/XAHByb2R1A'
    }

    cookies = {
        'SPC_F': 'mcQd8tnjG4Qi33FyqITty0qlWdd64v5p',
        'SPC_EC': '.dndDVEFOWTZoc0V2elFuVeKz7VTHi9etzKYy74Ieis1hhOaorSedb5kXlX8/A4QN0eDWrBhQYg5JNMpWm2qJNHA37Zja3dR1bwjSVT8RL6iVe789vpL1zwQJIwRPuE566q9s+6skcXwaCUkEmUJ+CxGu9HbatHJQ1KcxqWEpoqhEzedvcxhpxjGOZBCa/olbWhgVN1n6ZNDk6aEwN/BQzeiRzBKLS/EfMrAGTrWpL64=',
        'SPC_U': '227678781'
    }

    params = {
        'item_id': item_id,
        'shop_id': shop_id,
        'tz_offset_minutes': 420,
        'detail_level': 0
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gửi request: {e}")
        return None

def main():
    item_id = '24873905864'
    shop_id = '1053707688'
    
    result = get_shopee_product(item_id, shop_id)
    print(result)
    if result:
        print("Dữ liệu sản phẩm:", result)
    else:
        print("Không thể lấy dữ liệu sản phẩm")

if __name__ == "__main__":
    main()
