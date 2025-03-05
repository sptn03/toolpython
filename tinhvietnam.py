import requests
import json
url = "https://dev-online-gateway.ghn.vn/shiip/public-api/master-data/province"
headers = {
    "Content-Type": "application/json",
    "Token": "88bcb03e-f428-11ef-bb13-2a342a4da1fb"
}

response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    print("Request successful!")
    print(response.json())  
    with open("tinh.json", "w", encoding="utf-8") as f:
        json.dump(response.json(), f, ensure_ascii=False)
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)